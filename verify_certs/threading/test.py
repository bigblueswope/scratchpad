from threading import Thread
from time import sleep
from queue import Queue
import os
import json
import logging

import randori_api
from randori_api.rest import ApiException

configuration = randori_api.Configuration()

# replaced with iteration over token files
#configuration.access_token = os.getenv("RANDORI_API_KEY");

configuration.host = "https://alpha.randori.io"

r_api = randori_api.RandoriApi(randori_api.ApiClient(configuration))

format = '%(asctime)s: %(message)s'
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt='%H:%M:%S')


class cert_host:
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





def check_cert(cert_host_dict, qr, token):
    '''
    This function will be called with 2 args:
        1.  Dict with hostname and port
        2.  An empty queue to hold the results

        There is no return value because the results queue is available to the calling function
    '''
    
    cert_host_dict['hostname'] = token + " " + cert_host_dict['hostname'] 
    # putting the cert_host_dict in results queue just to show that it works
    qr.put(cert_host_dict)



def do_work_for_org(token):
    '''
        This is where we call iterate_hostnames into a list that we will then pass to the next function
        along with the queue qr in which to store the results of the lookups
    '''

    cert_hosts = [{'hostname': 'www.randori.com', 'port': 443}, {'hostname': 'expired.badssl.com', 'port': 443},
    {'hostname': 'wrong.host.badssl.com', 'port': 443}]
    #cert_hosts = output of iterate_hostnames

    num_host_threads = min(10, len(cert_hosts))


    # Each org will have it's own queue called qr
    qr = Queue()
    
    result = [token]
   
    logging.info("Logging the Token: {}".format(token))

    int_results = 0


    def host_worker(qr, token):
        while True:
            item2 = q2.get()
            check_cert(item2, qr, token)
            q2.task_done()


    q2 = Queue()
    for i in range(num_host_threads):
        u = Thread(target=host_worker, args=(qr,token))
        u.daemon = True
        u.start()

    
    for ch in cert_hosts:
        q2.put(ch)

    
    #Wait for all the hostnames to be processed.  
    q2.join()

    # this iterates over everything in the results queue as if it were a list 
    #   it does not consume the queue (i.e. the queue still contains all the items that were inserted)
    for thing in list(qr.queue):
        result.append(thing)
    
    # printing the results
    logging.info("Logging the result: {}".format(result))

    # superflous sleep so we can observe timing to see that 20 threads at a time are being processed by the #   main function call
    sleep(1)


if __name__ == '__main__':
        
    path = '/Users/bj/.tokens/'
    
    tokens = os.listdir(path)
    
    q1 = Queue()

    for token in tokens:
        q1.put(token)
    
    def worker():
        while True:
            item = q1.get()
            do_work_for_org(item)
            q1.task_done()
    
    # Use many threads (20 max, or one for each url)
    num_worker_threads = min(20, len(tokens))
    
    for i in range(num_worker_threads):
         t = Thread(target=worker)
         t.daemon = True
         t.start()
    
    q1.join()       # block until all tasks are done
    
