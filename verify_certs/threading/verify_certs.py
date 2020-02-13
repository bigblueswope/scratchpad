from __future__ import print_function
from copy import copy
from threading import Thread
from Queue import Queue
import base64
import concurrent.futures
import http.client
import json
import logging
import os
import socket
import ssl
import sys
import threading
import time


import randori_api
from randori_api.rest import ApiException

from keys.api_tokens import get_api_token

configuration = randori_api.Configuration()

org_name = os.getenv("RANDORI_ENV")

# replaced with iteration over token files
configuration.access_token = get_api_token(org_name);
#configuration.access_token = os.getenv("RANDORI_API_KEY");

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
            cert_status = 'Cert to Host Name Mismatch'
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



def get_cert_status(q, results):
    while not q.empty():
        cert_host_tuple = q.get()

        cert_host_index = cert_host_tuple[0]
        cert_host = cert_host_tuple[1]

        print('Get Cert Status for: {}'.format(cert_host.hostname))

        bad_cert_status = []
        
        ports = get_ports_for_ip(cert_host.ip_id)
        
        for port in ports:
            cert_status = ''
    
            # ports known to not have certs and just slow down the scanner
            if port in [21, 22, 25, 53, 80, 139, 445, 2082, 3389, 8080]:
                continue
    
            print('Checking {} {}'.format(cert_host.hostname, port))
            #logging.info('Checking {} {}'.format(cert_host.hostname, port))
    
            cert_status = check_cert(cert_host.hostname, port)
    
            if cert_status:
                
                cert_host.port = port
                
                cert_host.cert_status = cert_status
                
                print(cert_host.org_id, cert_host.hostname_id, cert_host.hostname, cert_host.ip_id, cert_status)
                #logging.info('{} {}'.format(cert_host.hostname, cert_status))
    
                bad_cert_status.append(copy(cert_host.__dict__))
        
        return bad_cert_status
    

def multi_thread_lookup(cert_hosts):
    #set up the queue to hold all the urls
    q = Queue(maxsize=0)
    # Use many threads (50 max, or one for each url)
    num_theads = min(20, len(cert_hosts))

    # Building results list same length as urls list
    results = [{} for x in cert_hosts]

    #Populating Queue with tasks
    #load up the queue with the cert_hosts to fetch and the index for each job (as a tuple):
    for i in range(len(cert_hosts)):
        #need the index and the url in each queue item.
        q.put((i,cert_hosts[i]))

    #Starting worker threads on queue processing
    for i in range(num_theads):
        logging.debug('Starting thread ', i)
        worker = Thread(target=get_cert_status, args=(q,results))
        worker.setDaemon(True)    #setting threads as "daemon" allows main program to
                                  #exit eventually even if these dont finish
                                  #correctly.
        worker.start()

    #now we wait until the queue has been processed
    q.join()
    logging.info('All tasks completed.')


    
def cert_verification(org_name):
    path = '/Users/bj/.tokens/'
    
    print('Processing {}'.format(org_name))
    #logging.info("Thread %s: starting", org_name)
    
    with open((path + org_name), 'r+') as f:
        for line in f:
            token = line.rstrip('\n').rstrip(',')

    configuration.access_token = token

    broken_cert_hosts= []
    
    cert_hosts = iterate_hostnames()
    
    host0 = cert_hosts[0]

    org_id = host0.org_id

    outfile = org_id + '.json'

    print("Org Id: {}".format(org_id))

    print("Count of hosts for {}: {}".format(org_name, len(cert_hosts)))
    
    if not (os.path.isfile(outfile)):
    
        for cert_host in cert_hosts:
            data = get_cert_status(cert_host)
        
            broken_cert_hosts.extend(data)
        
        with open(outfile, 'w') as f:
            json.dump(broken_cert_hosts, f)




if __name__ == '__main__':

    format = '%(asctime)s: %(message)s'
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt='%H:%M:%S')

    #TODO: Rewrite to use list of orgs from Keychain
    path = '/Users/bj/.tokens/'

    token_files = os.listdir(path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(cert_verification, token_files)


