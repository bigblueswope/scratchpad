import base64
import http.client
import json
import os
import socket
import ssl
import sys


import randori_api
from randori_api.rest import ApiException

from keys.api_tokens import get_api_token

configuration = randori_api.Configuration()

org_name = os.getenv("RANDORI_ENV")

# Normal scripts use the environment variable to set the API Key
#  because they only look at data for one Org
#  but this script will iterate over all API Keys
#  and replace this value for each one of them
#  because it is generating stats for ALL Orgs
configuration.access_token = get_api_token(org_name);
#configuration.access_token = os.getenv("RANDORI_API_KEY");

configuration.host = "https://alpha.randori.io"

r_api = randori_api.RandoriApi(randori_api.ApiClient(configuration))

class platform_host:
    def __init__(self, hostname_id, org_id, hostname, ip_id):
        self.hostname_id = hostname_id
        self.org_id = org_id
        self.hostname = hostname
        self.ip_id = ip_id
        self.port = ''
        self.cert_status = ''


def prep_query(query_object):
   iq = json.dumps(query_object).encode()
   query = base64.b64encode(iq)
   return query


###
#Sample output of get_ports_for_ip
###
'''{
   'confidence': 75,
   'deleted': False,
   'id': '56fb7d79-fe1d-4b0a-89d8-4f2c27eec6d4',
   'ip_id': 'b4f16be0-2bc6-44da-92b8-a9cbd0b05e34',
   'last_seen': datetime.datetime(2019, 12, 12, 3, 14, 13, 278251, tzinfo=tzutc()),
   'max_confidence': 75,
   'org_id': '89623ad5-6051-444f-aff4-529f7e7e2e70',
   'port': 8443,
   'protocol': 6,
   'seen_open': True,
   'state': 'open'
}'''


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



##########
# Sample output of by get_hostnames_for_ip
##########
'''
{'confidence': 75,
 'deleted': False,
 'hostname': 'www.kesslerwoundcare.com',
 'hostname_id': '2c985a29-7585-4041-a1f0-667065784952',
 'hostname_tags': {},
 'id': '2c985a29-7585-4041-a1f0-667065784952,b50db97e-6841-4d06-a2e6-31fcc28a9170',
 'ip_id': 'b50db97e-6841-4d06-a2e6-31fcc28a9170',
 'last_seen': datetime.datetime(2019, 12, 14, 11, 52, 42, 953908, tzinfo=tzutc()),
 'max_confidence': 75,
 'org_id': '89623ad5-6051-444f-aff4-529f7e7e2e70'}
 '''

ge_medium_conf_hosts = json.loads('''{
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

    platform_hosts = []
    
    more_targets_data= True
    offset = 0
    limit = 200
    sort = ['hostname']

    while more_targets_data:
        
        query = prep_query(ge_medium_conf_hosts)

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
            platform_hosts.append(platform_host(h.hostname_id, h.org_id, h.hostname, h.ip_id))
        
    return platform_hosts



def default_function():
    # 2020-01-29:
    # TODO: Looking at this code today it appears that this is a copy
    #   of the script I wrote to look for expired certificates that 
    #   I copied, intending to repurpose to a tool to generate
    #   statistics around IPs and Ports.  But I haven't changed the 
    #   functions to do that, so the name of this file and the code
    #   in the file do not match.  Just going to print something and
    #   exit here.

    print("This is not the script you're looking for.  Read the TODO in the source...")
    sys.exit(0)
    
    hosts = iterate_hostnames()
    

    for host in hosts:
        org_id = host.org_id
        
        outfile = org_id + ".json"
        
        if (os.path.isfile(outfile)):
            print('OrgID Exists: {}'.format(org_id))
            return

        ports = get_ports_for_ip(host.ip_id)
        
        for port in ports:

            cert_host.port = port
            
            cert_host.cert_status = cert_status
            
    
    if not (os.path.isfile(outfile)):
        with open(outfile, 'w') as f:
            json.dump(broken_cert_hosts, f)




if __name__ == '__main__':
    #TODO: REWRITE logic to use list of orgs in Keychain
    path = '/Users/bj/.tokens/'

    for filename in os.listdir(path):
        print('Processing {}'.format(filename))

        with open((path + filename), 'r+') as f:
            for line in f:
                token = line.rstrip('\n').rstrip(',')

        configuration.access_token = token
        default_function()
