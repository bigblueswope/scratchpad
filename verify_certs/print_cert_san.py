import base64
import csv
from copy import copy
from datetime import datetime, timedelta
import http.client
import json
import os
import platform
from queue import Queue
import socket
import ssl
import sys
import threading

import randori_api
from randori_api.rest import ApiException

from api_tokens import get_api_token



# Ports highly unlikely to be SSL enabled so skip these ports
skip_ports = [
    21, 22, 25, 53, 80, 139, 445, 631, 853, 995, 1080, 1433, 2001, 2082, 3000, 3306, 3389, 
    4444, 5000, 5001, 5004, 5222, 5280, 5601, 5900, 5901, 5984, 5985, 6000, 
    6001, 6379, 6543, 6601, 7777, 8000, 8005, 8008, 8009, 8080, 8088, 8089, 
    8194, 9012, 15672
]

configuration = randori_api.Configuration()

org_name = os.getenv("RANDORI_ENV")

configuration.access_token = get_api_token(org_name);

configuration.host = "https://alpha.randori.io"

r_api = randori_api.DefaultApi(randori_api.ApiClient(configuration))

class cert_host:
    def __init__(self, hostname_id, org_id, hostname):
        self.hostname_id = hostname_id
        self.org_id = org_id
        self.hostname = hostname
        self.ports = []
        self.cert_status = ''
        self.cert_expiration_date = ''
        self.url = ''
        self.platform_host_url = ''


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.check_hostname = True
ssl_context.load_default_certs()

if platform.system().lower() == 'darwin':
    import certifi
    ssl_context.load_verify_locations(
        cafile=os.path.relpath(certifi.where()),
        capath=None,
        cadata=None)
    
warn_intervals = [  (7, 'Cert Expire 7'),
                    (14, 'Cert Expire 14'),
                    (30, 'Cert Expire 30'),
                    (60, 'Cert Expire 60')
                 ]



def check_cert(cert_host, port):

    hostname = cert_host.hostname

    cert_status = ''

    try:
        with socket.create_connection((hostname, port),10) as sock: # socket timeout 10 seconds
            try:
                with ssl_context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    
                    cert = ssock.getpeercert()

                    print(hostname, cert['subjectAltName'])

                      
    
            except ssl.SSLCertVerificationError as e:
                pass

            finally:
                sock.close()
                return cert_status

    except (socket.timeout, socket.gaierror, ssl.SSLError, ConnectionResetError, ConnectionRefusedError, BrokenPipeError):
            pass
    
    except OSError as e: 
        if e.args[0] == 41:
            pass
    
    finally:
        return cert_status




def prep_query(query_object):
   iq = json.dumps(query_object).encode()
   query = base64.b64encode(iq)
   return query




def get_ports_for_ip(ip_id):

    ports_for_ip_query = json.loads('''{
        "condition": "AND",
        "rules": [
            {
                "field": "table.ip_id",
                "operator": "equal",
                "value": ""
            }
        ]
    }''')

    open_ports = []

    ports_for_ip_query['rules'][0]['value'] = ip_id

    offset = 0
    limit = 1000
    sort = ['port']

    q = prep_query(ports_for_ip_query)

    try:
        api_response = r_api.get_ports_for_ip(offset=offset, limit=limit, sort=sort, q=q)

        for port_details in api_response.data:
            
            if port_details.state == 'open' and port_details.port not in skip_ports:
            
                open_ports.append(port_details.port)

    except ApiException as e:
        
        print('Exception when calling DefaultApi->get_ports_for_ip:\n {e}')

    return open_ports



def get_ip_ids_for_hostname(hostname_id):

    host_id_to_ip_id_query = json.loads('''{
        "condition": "AND",
        "rules": [
            {
                "field": "table.hostname_id",
                "operator": "equal",
                "value": ""
            }
        ]
    }''')


    ip_ids = []

    offset = 0
    limit = 1000
    sort = ['hostname_id']

    host_id_to_ip_id_query['rules'][0]['value'] = hostname_id

    q = prep_query(host_id_to_ip_id_query)

    try:
         api_response = r_api.get_ips_for_hostname(offset=offset, limit=limit, sort=sort, q=q)
         
         for item in api_response.data:
            
            ip_ids.append(item.ip_id)
    
    except ApiException as e:
        
        print("Exception when calling RandoriApi -> get_ips_for_hostname: %s\n" % e)

    return ip_ids





def iterate_hostnames():

    hostnames_query = json.loads('''{
        "condition": "AND",
        "rules": [
            {
                "field": "table.confidence",
                "operator": "greater_or_equal",
                "value": 60
            }
        ]
    }''')


    hostnames = []

    cert_hosts = []

    more_targets_data= True

    offset = 0
    limit = 1000
    sort = ['hostname']

    while more_targets_data:
        
        query = prep_query(hostnames_query)

        try:
            resp = r_api.get_hostname(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            
            print("Exception in RandoriApi->get_hostname: %s\n" % e)
            
        
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
                
                cert_hosts.append(cert_host(h.id, h.org_id, h.hostname))
        
    return cert_hosts



def build_list_of_cert_hosts():

    cert_hosts = iterate_hostnames()

    org_id = cert_hosts[0].org_id

    for cert_host in cert_hosts:
        
        ip_ids = get_ip_ids_for_hostname(cert_host.hostname_id)
        
        for ip_id in ip_ids:
    
            ports = get_ports_for_ip(ip_id)

            for port in ports:

                cert_status = ''
    
                if port not in cert_host.ports:

                    cert_host.ports.append(port)
                
        source_q.put(cert_host)

    return org_id


    
def do_cert_work():
    while True:
        if not source_q.empty():
            
            cert_host = source_q.get()

            for port in cert_host.ports:
                
                check_cert(cert_host, port)
                
            source_q.task_done()


if __name__ == '__main__':

    broken_cert_hosts = []

    source_q = Queue()
    
    org_id = build_list_of_cert_hosts()

    num_worker_threads = min(60, source_q.qsize())
    
    for i in range(num_worker_threads):

        t = threading.Thread(target=do_cert_work)

        t.daemon = True

        t.start()
    
    source_q.join()       # block until all tasks are done
    
