import argparse
import os
import sys
import socket


from threading import Thread
from time import sleep
from queue import Queue


def resolve_list_of_hostnames(hostname_list):

    num_host_threads = min(100, len(hostname_list))

    results = []

    def host_worker():
        while True:
            # get a hostname out of the q2 queue
            hostname = q2.get()

            # resolve the hostname
            try:
                ip = socket.gethostbyname(hostname)
            except socket.gaierror:
                ip = ''
    
            # insert tuple of hostname and IP into the Results Queue
            results.append((hostname, ip))

            # notify the queue work is done
            q2.task_done()


    q2 = Queue()

    # fill the source queue with hostnames to be resolved
    for hostname in hostname_list:
        q2.put(hostname)

    # spin up threads
    for i in range(num_host_threads):
        
        # Create a thread 
        u = Thread(target=host_worker, args=[])

        #daemonize the thread
        u.daemon = True

        #start the thread
        u.start()

    
    #Wait for all the hostnames to be processed.  
    q2.join()

    return results


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Compare File With Domains to Existing Domains in Platform')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, help="File with possible additional domains")

    args = parser.parse_args()

    new_hostnames = []

    with open(args.input, 'r+') as f:
        for line in f:
            new_host = line.rstrip('\n').rstrip(',').lower()

            if new_host == 'domainname':
                continue
            
            new_hostnames.append(new_host)

    resolved_hosts = resolve_list_of_hostnames(new_hostnames)


    for resolved_host,resolution in resolved_hosts:
        print("%s: %s" % (resolved_host, resolution))
