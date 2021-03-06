from copy import copy
import base64
import http.client
import json
import os
import socket
import ssl
import sys


import randori_api
from randori_api.rest import ApiException

from api_tokens import get_api_token, get_orgs

configuration = randori_api.Configuration()

org_name = os.getenv("RANDORI_ENV")

configuration.access_token = get_api_token(org_name);

configuration.host = "https://alpha.randori.io"

r_api = randori_api.RandoriApi(randori_api.ApiClient(configuration))

class cert_host:
    def __init__(self, hostname_id, org_id, hostname, ip_id):
        self.hostname_id = hostname_id
        self.org_id = org_id
        self.hostname = hostname
        self.ip_id = ip_id
        self.port = ''
        self.cert_status = ''
        self.url = ''


def check_cert(hostname, port):
    connection = http.client.HTTPSConnection(hostname, port, timeout=10)

    try:
        connection.request("GET", "/")
        response = connection.getresponse()
        cert_status = ''
        connection.close()
    except ssl.SSLCertVerificationError as e:
        if e.verify_code == 10:
            cert_status = 'Expired Cert'
        elif e.verify_code == 62:
            cert_status = 'Cert Name Mismatch'
        elif e.verify_code == 18:
            cert_status = 'Self-Signed Cert'
        elif e.verify_code == 19:
            cert_status = 'Self-Signed CA'
        elif e.verify_code == 20:
            cert_status = ''
        else:
            print('Unknown SSL Cert Verification Error')
            print('Verification error code {}'.format(e.verify_code))
            print(e.verify_message)
    except (socket.timeout, socket.gaierror, ssl.SSLError, ConnectionResetError):
        cert_status = ''
    except http.client.BadStatusLine:
        cert_status = ''
    except ConnectionRefusedError:
        cert_status = ''
    finally:
        connection.close()

    return cert_status



def prep_query(query_object):
   iq = json.dumps(query_object).encode()
   query = base64.b64encode(iq)
   return query



ports_for_ip_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.ip_id",
      "operator": "equal",
      "value": ""
    }
  ],
  "valid": true
}
''')



def get_ports_for_ip(ip_id):
    open_ports = []

    ports_for_ip_query['rules'][0]['value'] = ip_id

    offset = 0
    limit = 200
    sort = ['port']
    reversed_nulls = True # bool | if true, sorts nulls as if smaller than any nonnull value for all sort parameters. otherwise (default) treats as if larger (optional)

    q = prep_query(ports_for_ip_query)

    try:
        api_response = r_api.get_ports_for_ip(offset=offset, limit=limit, sort=sort, q=q, reversed_nulls=reversed_nulls)

        for port_details in api_response.data:
            if port_details.state == 'open':
                open_ports.append(port_details.port)
    except ApiException as e:
        print("Exception when calling RandoriApi->get_ports_for_ip: %s\n" % e)

    return open_ports



initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    }
  ],
  "valid": true
}
''')

def iterate_hostnames():
    # preloading hostnames with connect.ushworks.com because it crashes the script
    hostnames = ['connect.ushworks.com']
    cert_hosts = []
    more_targets_data= True
    offset = 0
    limit = 200
    sort = ['hostname']

    while more_targets_data:
        
        query = prep_query(initial_query)

        try:
            resp = r_api.get_hostnames_for_ip(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_hostnames_for_ip: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_targets_data = False
        else:
            offset = max_records

        for h in resp.data:
            if h.hostname in hostnames:
                continue
            else:
                hostnames.append(h.hostname)
                cert_hosts.append(cert_host(h.hostname_id, h.org_id, h.hostname, h.ip_id))
        
    return cert_hosts



def cert_verification():
    broken_cert_hosts= []
    
    cert_hosts = iterate_hostnames()
    

    for cert_host in cert_hosts:
        org_id = cert_host.org_id
        
        outfile = "verify_certs/results/" + org_id + ".json"
        
        ports = get_ports_for_ip(cert_host.ip_id)
        
        for port in ports:
            cert_status = ''

            # ports known to not have certs and just slow down the scanner
            if port in [21, 22, 25, 53, 80, 139, 445, 2082, 3389, 8080]:
                continue

            print('Checking {} {}'.format(cert_host.hostname, port))

            cert_status = check_cert(cert_host.hostname, port)

            if cert_status:
                
                cert_host.port = port
                
                cert_host.cert_status = cert_status

                cert_host.url = ''.join( ['https://', cert_host.hostname, ':', str(cert_host.port)] )
                
                print(cert_host.org_id, cert_host.hostname_id, cert_host.hostname, cert_host.ip_id, cert_host.url, cert_status)
                
                broken_cert_hosts.append(copy(cert_host.__dict__))

    
    if not (os.path.isfile(outfile)):
        with open(outfile, 'w') as f:
            json.dump(broken_cert_hosts, f)




if __name__ == '__main__':
    for org in get_orgs():
        print('Processing {}'.format(org))

        configuration.access_token = get_api_token(org)

        cert_verification()
