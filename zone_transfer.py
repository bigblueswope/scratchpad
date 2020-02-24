import argparse
import dns.query
import dns.resolver
import dns.zone

import threading
from time import sleep
from queue import Queue



def try_zone_xfer(domain):

    print("%s Attempting Zone Transfer: %s" % (threading.currentThread().getName(), domain))
            
    try:
        soa_answer = dns.resolver.query(domain, 'SOA')
    except Exception as e:
        print("Exception in finding SOA for %s: %s" % (domain, str(e)))
        return []
    
    zone_server = soa_answer[0].mname
    
    try:
        master_answer = dns.resolver.query(zone_server, 'A')
    except Exception as e:
        print("Exeption resolving SOA to Address for %s: %s" % (zone_server, str(e)))
        return []

    zone_server_address = master_answer[0].address
    
    try:
        
        z = dns.zone.from_xfr(dns.query.xfr(zone_server_address, domain))
        
        # Iterate over the 'A' records in the zone transfer
        for (name, _, _) in z.iterate_rdatas(rdtype='A'):
            
            name = str(name)
            
            if "@" in name:
                continue
            
            fqdn = '.'.join((name, domain)) 
            
            xfer_hosts.append(fqdn)

    except Exception as e:
        print("Exception transferring domain %s: %s" % (domain, str(e)))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Attempt DNS Zone Transfers of domains in a file')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, help="File domains to attempt to transfer")
    optional.add_argument("-o", "--output", default=False,
        help="If the output arg/flag is provided, write transferred 'A' records to outfile.")
    parser._action_groups.append(optional)

    args = parser.parse_args()
    
    xfer_hosts = []

    doms_q = Queue()

    with open(args.input, 'r+') as f:

        for line in f:

            domain = line.lstrip('*.').rstrip('\n.,')
            
            if domain == 'domainName':
                continue
            
            doms_q.put(domain)

    def worker():
        while not doms_q.empty():
            
            dom = doms_q.get()
            
            try_zone_xfer(dom)
            
            doms_q.task_done()

    # Use many threads (20 max, or one for each domain, which ever is less)
    num_worker_threads = min(20, doms_q.qsize())

    for i in range(num_worker_threads):
         t = threading.Thread(target=worker)
         t.daemon = True
         t.start()

    doms_q.join()       # block until all tasks are done


    print(xfer_hosts)

    if args.output:
        with open(args.output, 'w+') as outfile:
            for host in xfer_hosts:
                outfile.write("%s\n" % (host))

