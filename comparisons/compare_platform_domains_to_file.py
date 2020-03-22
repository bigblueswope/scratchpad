import argparse
import base64
import datetime
import json
import os
import sys
import socket

import common_functions
import entity_detector


#Note:
#  Instead of print statements, much of the output uses
#  sys.stderr.write
#  This is so you can pipe the output of domains that need to be added
#      into another program or redirect to a file (which can be done 
#      by providing a -o outfile argument too).


#Initial Query:
#    Name Type = Domain
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.name_type",
      "operator": "equal",
      "value": 0
    }
  ],
  "valid": true
}''')




def get_platform_domains():
    
    platform_domains = {}

    more_data= True
    offset = 0
    limit = 1000
    sort = ['hostname']

    query = common_functions.prep_query(initial_query)

    while more_data:
        
        try:
            resp = common_functions.r_api.get_hostname(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except common_functions.ApiException as e:
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

    parser._action_groups.append(optional)

    args = parser.parse_args()

    platform_domains = get_platform_domains()
    
    both_domains = {}
    addl_domains = []
    non_domain_entities = []
    count_of_input_items = 0
    count_of_unique_input_items_not_in_platform = 0

    
    with open(args.input, 'r+') as f:

        for line in f:

            new_domain = common_functions.line_cleaner(line)

            if not new_domain: 
                continue
            
            # Number of lines in input file
            count_of_input_items += 1

            entity_type, _, _ = entity_detector.detect_entity(new_domain)

            if not entity_type == 'domains':
                non_domain_entities.append(new_domain)
                continue

            # host/domain does not exist in the Platform and is not a 
            #   duplicate in the input file
            if not new_domain in platform_domains.keys() and not new_domain in addl_domains:
                
                count_of_unique_input_items_not_in_platform += 1

                # append domain/host from file to list of domains to add to the platform
                #   so we can check for dupliates as we iterate over the file
                addl_domains.append(new_domain)

            else:
                # domain/host is already in the platform so create an entry in 
                #   the existing domain dictionary with a value of the Confidence
                try:
                    both_domains[new_domain] = platform_domains[new_domain]
                except KeyError:
                    # new_domain is a duplicate in the input file
                    #   not an existing Platform host/domain
                    #   so we don't add it to the list of "in both places"
                    pass
    
    sys.stderr.write("\n###################\nDomains To Be Added:\n\n")

    for dom in addl_domains:
        print(dom)

    # will write the domains to be added to an outfile
    if args.output:
        with open(args.output, 'w+') as outfile:
            for dom in addl_domains:
                outfile.write("%s\n" % (dom))
            
    sys.stderr.write("\nCount of items in input file: %i\n" % count_of_input_items)
    
    sys.stderr.write("\nCount of unique items in input file and not in platform: %i\n" % count_of_unique_input_items_not_in_platform)
    
    sys.stderr.write("\nCount of domains in Platform and input file: %i\n" % len(both_domains))

    sys.stderr.write("\nCount of non-domain entities in input file: %i\n" % len(non_domain_entities))

    sys.stderr.write("\nItems and their confidence in both Platform and input file: %s\n" % both_domains)

    
