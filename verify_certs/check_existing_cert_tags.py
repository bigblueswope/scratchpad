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

hostnames = []

hosts_w_existing_cert_issues = {}

broken_cert_hosts = []

stale_host_tags =[]

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


class untag_host:
    def __init__(self, hostname_id, tag_to_remove):
        self.hostname_id = hostname_id
        self.tag_to_remove = tag_to_remove


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
ssl_context.verify_mode = ssl.CERT_REQUIRED
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

cert_statuses = [ 'Cert Expired', 'Cert IP mismatch', 
                'Cert Name Mismatch', 'Cert Self-Signed', 
                'CA Self-Signed', 'Cert Expire 7',
                'Cert Expire 14', 'Cert Expire 30',
                'Cert Expire 60' ] 


# This is here because when testing I tweak the 60 day cert warning to 1060 and forget to set it back to 60
assert warn_intervals[3][0] == 60, 'warn_intervals 60 is wrong value. reset it and try again'



def remove_tags(host_id, tag):
    
    ops = json.loads('''[
        {
            "op": "remove",
            "path": "/tags/YOUR_TAG_HERE",
            "value": {}
        }
    ]''')

    query = json.loads('''{
        "condition": "OR",
        "rules": [
            {
                "field": "table.id",
                "operator": "equal",
                "value": "REPLACE_ME_WITH_HOST_ID"
            }
        ]
    }''')

    ops[0]['path'] = f"/tags/{tag}"

    query['rules'][0]['value'] = host_id
    
    hostname_patch_input = randori_api.HostnamePatchInput(operations=ops, q=query)

    try:
        
        api_response = api_instance.patch_hostname(hostname_patch_input=hostname_patch_input)
        
    except ApiException as e:
        
        print(f"Exception when removing tag {tag} from host_id {host_id} calling DefaultApi->patch_hostname:\n{e}")




def tag_hosts():
    
    global broken_cert_hosts

    ops = json.loads('''[
        {
            "op": "add",
            "path": "/tags/YOUR TAG HERE",
            "value": {}
        }
    ]''')

    query = json.loads('''{
        "condition": "OR",
        "rules": [
            {
                "field": "table.id",
                "operator": "equal",
                "value": "HOST ID HERE"
            }
        ]
    }''')
    
    
    for host in broken_cert_hosts:

        ops[0]['path'] = f"/tags/{host['cert_status']}"

        query['rules'][0]['value'] = host['hostname_id']

        hostname_patch_input = randori_api.HostnamePatchInput(operations=ops, q=query)

        try:
            api_response = r_api.patch_hostname(hostname_patch_input=hostname_patch_input)
            
        except ApiException as e:
            
            print(f"Exception when calling r_api.patch_hostname: {host['hostname']} with {host['cert_status']} \n {e}")



def find_tagged_hosts(tag_value):

    tag_query = json.loads('''
{
  "condition": "AND",
  "rules": [
    {
      "field": "table.tags",
      "operator": "has_key",
      "value": "TAG VALUE HERE"
    }
  ]
}
''')

    tag_query['rules'][0]['value'] = tag_value
    
    global hosts_w_existing_cert_issues

    more_targets_data = True

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
            
            try:
                
                hosts_w_existing_cert_issues[h.id].append(tag_value)

            except KeyError:
                
                hosts_w_existing_cert_issues[h.id] = [tag_value]




def check_cert(cert_host, port):

    hostname = cert_host.hostname

    print(hostname, port)

    cert_status = ''

    try:
        with socket.create_connection((hostname, port),10) as sock: # socket timeout 10 seconds
            try:
                with ssl_context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    
                    cert = ssock.getpeercert()

                    cert_host.cert_expiration_date = cert['notAfter']
                      
                    expiration_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    
                    for interval in warn_intervals:
                        
                        warn_date_time = datetime.now() + timedelta(interval[0])
                    
                        if expiration_date < warn_date_time:
                            
                            cert_status = interval[1]

                            sock.close()
    
                            return cert_status
    
            except ssl.SSLCertVerificationError as e:
                if e.verify_code == 10:
                    cert_status = 'Cert Expired'
                    
                elif e.verify_code == 64:
                    cert_status = 'Cert IP mismatch'
                    
                elif e.verify_code == 62:
                    cert_status = 'Cert Name Mismatch'
                    
                elif e.verify_code == 18:
                    cert_status = 'Cert Self-Signed'
                    
                elif e.verify_code == 19:
                    cert_status = 'CA Self-Signed'
                    
                elif e.verify_code == 20:
                    print(f'{hostnanme} {port} SSL verify code 20: {e.verify_message}')
                else:
                    print('Unknown SSL Cert Verification Error')
                    print(f'Verification error code {e.verify_code}')
                    print(e.verify_message)
            finally:
                sock.close()
                return cert_status

    except (socket.timeout, socket.gaierror, ssl.SSLError, 
            ConnectionResetError, ConnectionRefusedError, BrokenPipeError):
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


    global hostnames

    cert_hosts = []

    more_targets_data = True

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

            print("Ports for %s: %s" % (cert_host.hostname, ports))
            
            for port in ports:

                cert_status = ''
    
                if port not in cert_host.ports:

                    cert_host.ports.append(port)
                
        source_q.put(cert_host)

    return org_id


    
def do_cert_work():
    
    global hosts_w_existing_cert_issues

    global broken_cert_hosts
    
    global stale_host_tags

    while True:
        
        if not source_q.empty():
            
            cert_host = source_q.get()
            
            for port in cert_host.ports:
                #
                #  Each port can have a different certificate issue
                #    Collect all certificate issues into a list
                #    Iterate over the list, compare to existing tags
                #    If new, queue up new tag
                #   
                #    Then do the opposite
                #    Iterate over the existing tags, if the existing tag 
                #    no longer applies, queue up the tag removal
                #
                #  4 Lists: Current_Tags, Previous_Tags, Net_New_Tags, Expired_Tags
                #    Current_Tags - Previous_Tags = Net_New_Tags
                #    Previous_Tags - Current_Tags = Expired_Tags
                #
                cert_status = check_cert(cert_host, port)
                
                if cert_status:
                    
                    host_id = cert_host.hostname_id
                    
                    try:
                        
                        if not cert_status in hosts_w_existing_cert_issues[host_id]:
                            
                            needs_tagging = True
                            
                            #if we get to this point the host was previously tagged with one or more certificate issues
                            #  but the previous tag(s) no longer apply so remove them
                            
                            for tag_to_remove in hosts_w_existing_cert_issues[host_id]:
                                
                                stale_host_tags.append(untag_host(host_id, tag_to_remove))
                    
                    except KeyError:
                        
                        needs_tagging = True
                    
                    if needs_tagging:
                        
                        cert_host.cert_status = cert_status
                    
                        cert_host.url = ''.join( ['https://', cert_host.hostname, ':', str(port)] )
                        
                        cert_host.platform_host_url = ''.join( ['https://alpha.randori.io/' , str(short_name), '/hostnames/', str(host_id) ] ) 
                          
                        print(','.join([cert_host.cert_status, cert_host.platform_host_url, cert_host.hostname, cert_host.url, cert_host.cert_expiration_date]))
                            
                        broken_cert_hosts.append(copy(cert_host.__dict__))
                
                else:
                    # the 
                    try:
                        
                        for tag_to_remove in hosts_with_existing_cert_issues[host_id]:
                            
                            stale_host_tags.append(untag_host(host_id, tag_to_remove))
                        
                    except KeyError:
                        
                        pass
                    
            source_q.task_done()



if __name__ == '__main__':

    short_name = input("Org Short Name?: ")
    
    source_q = Queue()
    
    org_id = build_list_of_cert_hosts()

    print("Queue length: %s" % source_q.qsize())

    num_worker_threads = min(60, source_q.qsize())
    
    for i in range(num_worker_threads):

        t = threading.Thread(target=do_cert_work)

        t.daemon = True

        t.start()
    
    source_q.join()       # block until all tasks are done
    
    tag_hosts(broken_cert_hosts)

    dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    json_outfile = f'results/cert_issues_{org_id}_{dt}.json'

    try:
        
        with open(json_outfile, 'w') as f:
        
            json.dump(broken_cert_hosts, f)
            
            print(f'JSON Outfile: {json_outfile}')

    except FileNotFoundError:
        
        print(f'Could not write results to {json_outfile}')

        pass
    

    csv_outfile = f'results/cert_issues_{org_id}_{dt}.csv'

    try:
        
        with open(csv_outfile,'w') as f:
        
            # Using dictionary keys as fieldnames for the CSV file header
            writer = csv.DictWriter(f, broken_cert_hosts[0].keys())
            
            writer.writeheader()
            
            for d in broken_cert_hosts:
                
                writer.writerow(d)

        print(f'CSV Outfile: {csv_outfile}')

    except FileNotFoundError:

        print(f'Could not write results to {csv_outfile}')

        pass
