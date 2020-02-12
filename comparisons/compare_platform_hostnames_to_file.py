import argparse
import base64
import datetime
import json
import os
import sys
import socket

import randori_api
from randori_api.rest import ApiException

from libs.threaded_name_resolution import resolve_list_of_hostnames

#Note:
#  Instead of print statements, much of the output uses
#  sys.stderr.write
#  This is so you can pipe the output of domains that need to be added
#      into another program or redirect to a file (which can be done 
#      by providing a -o outfile argument too).

configuration = randori_api.Configuration()

configuration.access_token = os.getenv("RANDORI_API_KEY");

configuration.host = "https://alpha.randori.io"

r_api = randori_api.RandoriApi(randori_api.ApiClient(configuration))


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



def prep_query(query_object):

   iq = json.dumps(query_object).encode()

   query = base64.b64encode(iq)

   return query


def resolve_hostnames(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        if ip:
            return ip
        else:
            return False
    except socket.gaierror:
        return False



def get_platform_ips():
    platform_ips = {}

    more_data= True
    offset = 0
    limit = 200
    sort = ['ip']

    while more_data:

        query = prep_query(initial_query)

        try:
            resp = r_api.get_ip(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_hostname: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit

        if resp.total <= max_records:
            more_data = False
        else:
            offset = max_records

        for item in resp.data:
            if not item.ip in platform_ips.keys():
                platform_ips[item.ip] = item.confidence

    return platform_ips



def get_platform_domains():
    
    platform_domains = {}

    more_data= True
    offset = 0
    limit = 200
    sort = ['hostname']

    while more_data:
        
        query = prep_query(initial_query)

        try:
            resp = r_api.get_hostname(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_hostname: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_data = False
        else:
            offset = max_records

        for item in resp.data:
            if not item.hostname in platform_domains.keys():
                platform_domains[item.hostname] = item.confidence

    return platform_domains




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Compare File With Domains to Existing Domains in Platform')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, help="File with possible additional domains")
    optional.add_argument("-o", "--output", default=False, 
        help="If the output arg/flag is provided, write missing domains to outfile.")
    optional.add_argument("-r", "--resolution", action='store_true', default=False,
        help="If the resolution arg/flag is provided, print the IP with the hostname")
    optional.add_argument("-n", "--name_first", action='store_true', default=False,
        help="If resolution flag is true, print the name first instead of the resolution")
    parser._action_groups.append(optional)

    args = parser.parse_args()

    platform_domains = get_platform_domains()
    platform_ips = get_platform_ips()
    
    new_domains = {}
    new_ips = {}
    both_domains = {}
    both_ips = {}

    addl_domains = []
    
    count_of_input_items = 0
    count_of_unique_input_items_not_in_platform = 0
    new_dom_count = 0
    non_resolving_dom_count = 0
    hosts_wo_ips_in_platform = 0

    
    with open(args.input, 'r+') as f:
        for line in f:
            new_hostname = line.rstrip('\n').rstrip(',')

            if new_hostname == 'domainName':
                continue
            
            count_of_input_items += 1

            # host/domain does not exist in the Platform and is not a 
            #   duplicate in the input file
            if not new_hostname in platform_domains.keys() and not new_hostname in addl_domains:
                
                count_of_unique_input_items_not_in_platform += 1

                # append domain/host from file to list of domains to add to the platform
                #   so we can check for dupliates as we iterate over the file
                addl_domains.append(new_hostname)
            
            else:
                # domain/host is already in the platform so create an entry in 
                #   the existing domain dictionary with a value of the Confidence
                try:
                    both_domains[new_hostname] = platform_domains[new_hostname]
                except KeyError:
                    # new_domain is a duplicate in the input file
                    #   not an existing Platform host/domain
                    #   so we don't add it to the list of "in both places"
                    continue
    

    for hn, ip in resolve_list_of_hostnames(addl_domains):
        
        if ip:
            try:
                # The host/domain resolved to an IP we already know about
                # No need to add that host/domain because we have a host/domain
                # that will get us to the IP.  Just increment the counter
                new_ips[ip] +=1
            
            except KeyError:
                # The IP for the host/domain is not in platform and
                #   the IP has not resolved for any new hosts/domains
                #   So add it to the new_ips dict
                new_ips[ip] = 1
                
                # Also add it to the new hosts/domains dict
                new_domains[hn] = ip
                
                # increment the count of hosts/domains we will be
                #   adding to the platform
                new_dom_count += 1
        else:
            # Increment the count of non-resolving hosts/domains
            non_resolving_dom_count += 1
                    
    sys.stderr.write("\n###################\nDomains To Be Added:\n\n")

    for dom,dom_ip in new_domains.items():
        try:
            # if confidence of ip in platform is greater than specified integer
            if platform_ips[dom_ip] >= 60:
                # we do not need to add the host/domain name to the platform
                #  so add an entry to the both_ips dict
                both_ips[dom_ip] = platform_ips[dom_ip]
                #because we already know about the IP iterate to next item
                continue
        except KeyError:
            # The IP of the host/domain is not in the platform
            #   so continue with this iteration
            pass
        
        # count of host/domain names that resolve but the IP 
        #    is not in the platform
        hosts_wo_ips_in_platform += 1

        # uses print here which writes to stdout which can be piped to another program

        # If we want to see the IP of the host/domain in the output
        if args.resolution:
            # If we want to see the host/domain before the IP 
            if args.name_first:
                print(dom, dom_ip)
            else:
                print(dom_ip, dom)
        else:
            print(dom)
    

    # will write the domains to be added to an outfile
    if args.output:
        with open(args.output, 'w+') as outfile:
            for dom,dom_ip in new_domains.items():
                if args.resolution:
                    if args.name_first:
                        outfile.write("%s %s\n" % (dom,dom_ip))
                    else:
                        outfile.write("%s %s\n" % (dom_ip,dom))
                else:
                        outfile.write("%s\n" % (dom))
            
    sys.stderr.write("\nCount of hostnames in input file: %s\n" % str(count_of_input_items))
    
    sys.stderr.write("\nCount of unique hostnames in input file and not in platform: %s\n" % str(count_of_unique_input_items_not_in_platform))
    
    sys.stderr.write("\nCount of hostnames in Platform and input file: %s\n" % str(len(both_domains)))

    sys.stderr.write("\nCount of hostnames in input file with unique IPs: %s\n" % str(new_dom_count))
    
    sys.stderr.write("\nCount of hostnames that do not have IPs in Platform and will be added to Platform: %s\n" % str(hosts_wo_ips_in_platform))

    sys.stderr.write("\nCount of non-resolving hostsnames not in Platform: %s\n" % str(non_resolving_dom_count))

    sys.stderr.write("\nHostnames and their Confidence in both Platform and input file: %s\n" % both_domains)

    sys.stderr.write("\nIPs and their Confidence in both Platform and input file: %s\n" % both_ips)
    
