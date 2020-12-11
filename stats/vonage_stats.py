import argparse
import base64
import ipaddress
import json
import os
import sys

import common_functions
import entity_detector

#Initial Query:
#    Confidence Greater Than or Equal To Medium
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
}''')



def get_counts(endpoint, verbose):

    results = []

    domain_count = 0

    hostname_count = 0

    potential_ip_count = 0

    funct_name = 'get_' + endpoint
    
    more_targets_data = True

    if endpoint == 'network':
        initial_query['rules'][0]['value'] = 0
    
    offset = 0
    limit = 1000
    sort = ['confidence']
    
    query = common_functions.prep_query(initial_query)
    
    while more_targets_data:
        
        try:
            da_funct = getattr(common_functions.r_api, funct_name)
    
            resp = da_funct(offset=offset, limit=limit,
                                    sort=sort, q=query)
    
        except common_function.ApiException as e:
    
            print("Exception in RandoriApi->%s: %s\n" % (funct_name,e))
    
            sys.exit(1)
    
        max_records = offset + limit

        if resp.total <= max_records:
            more_targets_data = False
        else:
            offset = max_records

        for result in resp.data:
            results.append(result)

    
    if endpoint == 'hostname':
        
        for entity in results:
        #for entity in results.data:
            
            entity_type = entity_detector.detect_entity(entity.hostname)[0]

            if entity_type == 'hostnames':
                
                hostname_count += 1

            elif entity_type == 'domains':

                domain_count += 1
    
        print("Domains: ", domain_count)

        print("Hostnames: ", hostname_count)

    if endpoint == 'network':
        
        for network in results:
            try:
                for ip in ipaddress.IPv4Network(network.network):
                    potential_ip_count += 1
            except ipaddress.AddressValueError:
                pass

        print("Potential IP Count:", potential_ip_count)

    if not verbose:

        print("%i" % resp.total)

    else:

        print("%ss: %i" % (endpoint, resp.total))



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'A script to retrieve total counts of entities')

    optional = parser._action_groups.pop()

    optional.add_argument("-e", "--endpoint", default=False,
        help="If the endpoint arg is provided, only show the total for the specified endpoint.")

    optional.add_argument ("-l", "--list_endpoints", action='store_true', default=False,
        help="If the list_endpoints argument is provided, print the available endpoints and exit.")

    optional.add_argument ("-v", "--verbose", action='store_true', default=False,
        help="If quiet flag is given, do not print endpoint names, print just the counts.")

    parser._action_groups.append(optional)

    args = parser.parse_args()

    api_endpoints = [ 'target', 'service', 'hostname', 'ip', 'network']
    
    if args.list_endpoints:
        print("Possible endpoints:\n%s" % api_endpoints)
        sys.exit(0)

    if args.endpoint:

        get_counts(args.endpoint, args.verbose)

    else:

        for endpoint in api_endpoints:

            get_counts(endpoint, args.verbose)



    '''
    Domains
    Sub-domains
    IP addresses
    Hosts
    Certificates
    ''' 
