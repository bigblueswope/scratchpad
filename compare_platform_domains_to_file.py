from __future__ import print_function
import argparse
import base64
import datetime
import json
import logging
import logging.handlers
import os
from pathlib import Path
import sys
import socket

import randori_api
from randori_api.rest import ApiException

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
#    Confidence Greater Than or Equal To Medium
#    and
#    Target Temptation Greater Than or Equal To High
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



##########
# Sample JSON returned by get_hostname
##########
'''
{'confidence': 75,
 'deleted': False,
 'first_seen': datetime.datetime(2019, 9, 13, 20, 18, 45, 334601, tzinfo=tzutc()),
 'hostname': 'www.webernets.online',
 'id': 'bc6a641f-eef5-444f-9311-1d43da55638c',
 'ip_count': 15,
 'last_seen': datetime.datetime(2019, 10, 7, 12, 25, 56, 107949, tzinfo=tzutc()),
 'max_confidence': 75,
 'name_type': 1,
 'org_id': '71803330-934a-4c4d-bd82-af1ba5e73ae8',
 'tags': {},
 'target_temptation': 22}
 '''

def resolve_hostnames(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        if ip:
            return ip
        else:
            return False
    except socket.gaierror:
        return False

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

        for host in resp.data:
            if not host.hostname in platform_domains.keys():
                platform_domains[host.hostname] = host.confidence

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

    addl_domains = []
    both_domains = {}
    
    sys.stderr.write("\n###################\nDomains from Input file:\n\n")

    with open(args.input, 'r+') as f:
        for line in f:
            # new_domain = line from file
            new_domain = line.rstrip('\n').rstrip(',')
            if new_domain == 'domainName':
                continue

            sys.stderr.write("%s\n" % new_domain)

            if not new_domain in platform_domains.keys():
                # append domain/host from file to list of domains to add to the platform
                addl_domains.append(new_domain)
            else:
                # domain/host is already in the platform so create an entry in 
                #   the existing domain dictionary with a value of the Confidence
                both_domains[new_domain] = platform_domains[new_domain]
    
    sys.stderr.write("\n###################\nDomains To Be Added:\n\n")

    new_dom_count = 0
    non_resolving_dom_count = 0

    # uses print here which writes to stdout which can be piped to another program
    for dom in addl_domains:
        ip = resolve_hostnames(dom)
        if ip:
            new_dom_count += 1
            if args.resolution:
                if args.name_first:
                    print(dom, ip)
                else:
                    print(ip, dom)
            else:
                print(dom)
        else:
            non_resolving_dom_count += 1
    
    # will write the domains to be added to an outfile
    if args.output:
        with open(args.output, 'w+') as outfile:
            for dom in addl_domains:
                outfile.write(dom)
                outfile.write('\n')
            
    sys.stderr.write("\nCount of Non-Resolving Domains not in Platform: %s\n" % str(non_resolving_dom_count))

    sys.stderr.write("\nCount of Domains that need to be added: %s\n" % str(new_dom_count))

    sys.stderr.write("\nCount of Domains in Platform and Input file: %s\n" % str(len(both_domains)))

    sys.stderr.write("\nDomains and their Confidence in both Platform and Input file: %s\n" % both_domains)
    
