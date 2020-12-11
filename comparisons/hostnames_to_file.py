import argparse
import base64
import datetime
import json
import os
import sys
import socket

from threaded_name_resolution import resolve_list_of_hostnames

import common_functions
import entity_detector

#Note:
#  Instead of print statements, much of the output uses
#  sys.stderr.write
#  This is so you can pipe the output of hosts that need to be added
#      into another program or redirect to a file (which can be done 
#      by providing a -o outfile argument too).


#Initial Query:
#    Confidence Greater Than or Equal To 0
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 0
    }
  ],
  "valid": true
}
''')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Compare File With Hostnames to Existing Hostnames in Platform')

    optional = parser._action_groups.pop()

    required = parser.add_argument_group('required arguments')

    required.add_argument("-i", "--input", required=True, help="File with possible additional hosts")

    optional.add_argument("-o", "--output", default=False, 
        help="If the output arg/flag is provided, write missing hosts to outfile.")

    optional.add_argument("-r", "--resolution", action='store_true', default=False,
        help="If the resolution arg/flag is provided, print the IP with the hostname")

    optional.add_argument("-n", "--name_first", action='store_true', default=False,
        help="If resolution flag is true, print the name first instead of the resolution")

    parser._action_groups.append(optional)

    args = parser.parse_args()

    new_hosts = {}
    new_ips = {}
    both_hosts = {}
    both_ips = {}

    addl_hosts = []
    hosts_wo_parents = []
    non_hostnames = []
    
    count_of_input_items = 0
    count_of_unique_input_items_not_in_platform = 0
    new_host_count = 0
    non_resolving_host_count = 0
    hosts_wo_ips_in_platform = 0
    
    p_hosts = common_functions.get_hosts(initial_query)
    
    platform_hosts = {}

    for item in p_hosts:
        platform_hosts[item.hostname] = item.confidence
    
    p_ips = common_functions.get_ips(initial_query)
    
    platform_ips = {}

    for item in p_ips:
        platform_ips[item.hostname] = item.confidence

    
    platform_domains = []
    
    for entity in platform_hosts.keys():
        
        ent_type, ent_name, domain = entity_detector.detect_entity(entity)

        if ent_type == 'domains':
            platform_domains.append(domain)
    
    
    with open(args.input, 'r+') as f:

        for line in f:

            new_hostname = common_functions.line_cleaner(line)

            if not new_hostname:
                continue

            count_of_input_items += 1
            
            ent_type, ent_name, domain = entity_detector.detect_entity(new_hostname)

            if ent_type != 'hostnames':
                if ent_type == 'domains' and domain in platform_domains:
                    continue
                if not new_hostname in non_hostnames:
                    non_hostnames.append(new_hostname)
                continue
            
            if not domain in platform_domains:
                if not new_hostname in hosts_wo_parents:
                    hosts_wo_parents.append(new_hostname)
                continue
            
            # host/hostname does not exist in the Platform and is not a duplicate in the input file

            if not new_hostname in platform_hosts and not new_hostname in addl_hosts:
                
                count_of_unique_input_items_not_in_platform += 1

                # append hostname/host from file to list of hosts to add to the platform
                #   so we can check for dupliates as we iterate over the file
                addl_hosts.append(new_hostname)
            
            else:
                # hostname/host is already in the platform so create an entry in 
                #   the existing hostname dictionary with a value of the Confidence
                try:
                    both_hosts[new_hostname] = platform_hosts[new_hostname]
                except KeyError:
                    # new_hostname is a duplicate in the input file
                    #   not an existing Platform host/hostname
                    #   so we don't add it to the list of "in both places"
                    continue
    

    for hn, ip in resolve_list_of_hostnames(addl_hosts):
        
        if ip:
            try:
                # The host/hostname resolved to an IP 
                # increment the counter
                new_ips[ip] +=1
            
            except KeyError:
                # The IP for the host/hostname is not in platform and
                #   the IP has not resolved for any new hosts/hosts
                #   So add it to the new_ips dict
                new_ips[ip] = 1
                
                # Also add it to the new hosts/hosts dict
                new_hosts[hn] = ip
                
                # increment the count of hosts/hosts we will be
                #   adding to the platform
                new_host_count += 1
        else:
            # Increment the count of non-resolving hosts/hosts
            non_resolving_host_count += 1
                    
    sys.stderr.write("\n###################\nHostnames To Be Added:\n\n")

    for host,host_ip in new_hosts.items():
        try:
            # if confidence of ip in platform is greater than specified integer
            if platform_ips[host_ip] >= 60:
                # we do not need to add the host/hostname name to the platform
                #  so add an entry to the both_ips dict
                both_ips[host_ip] = platform_ips[host_ip]
                #because we already know about the IP iterate to next item
                continue
        except KeyError:
            # The IP of the host/hostname is not in the platform
            #   so continue with this iteration
            pass
        
        # count of host/hostname names that resolve but the IP 
        #    is not in the platform
        hosts_wo_ips_in_platform += 1


        # If we want to see the IP of the host/hostname in the output
        if args.resolution:
            # If we want to see the host/hostname before the IP 
            if args.name_first:
                print(host, host_ip)
            else:
                print(host_ip, host)
        else:
            print(host)
    

    # will write the hosts to be added to an outfile
    if args.output:
        with open(args.output, 'w+') as outfile:
            for host,host_ip in new_hosts.items():
                if args.resolution:
                    if args.name_first:
                        outfile.write("%s %s\n" % (host,host_ip))
                    else:
                        outfile.write("%s %s\n" % (host_ip,host))
                else:
                    outfile.write("%s\n" % (host))
            
    sys.stderr.write("\nCount of hostnames in input file: %i\n" % count_of_input_items)
    
    sys.stderr.write("\nCount of unique hostnames in input file and not in platform: %i\n" % count_of_unique_input_items_not_in_platform)
    
    sys.stderr.write("\nCount of hostnames in Platform and input file: %i\n" % len(both_hosts))

    sys.stderr.write("\nCount of hostnames in input file with unique IPs: %i\n" % new_host_count)
    
    sys.stderr.write("\nCount of hostnames that do not have IPs in Platform and will be added to Platform: %i\n" % hosts_wo_ips_in_platform)

    sys.stderr.write("\nCount of non-hostnames input file: %i\n" % len(non_hostnames))

    sys.stderr.write("\nCount of non-resolving hostnames not in Platform: %i\n" % non_resolving_host_count)
    
    sys.stderr.write("\nCount of hosts without parent domains in Platform: %i\n" % len(hosts_wo_parents))

    #sys.stderr.write("\nHostnames in both Platform and input file: %s\n" % both_hosts)

    #sys.stderr.write("\nIPs and their Confidence in both Platform and input file: %s\n" % both_ips)
    
    sys.stderr.write("\nHosts without parent domains in Platform: %s\n" % hosts_wo_parents)
    
    sys.stderr.write("\nNon-Hostnames: %s\n" % non_hostnames)
