import argparse
import base64
import json
import os
import sys

import common_functions


#Initial Query:
#    Confidence Greater Than or Equal To Zero
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
}''')



def get_sample_output(funct_name):
    offset = 0
    limit = 1
    sort = ['confidence']

    #if funct_name == 'statistics':
    #    initial_query = ''

    query = common_functions.prep_query(initial_query)

    
    try:
        da_funct = getattr(common_functions.r_api, funct_name)

        resp = da_funct(offset=offset, limit=limit,
                                sort=sort, q=query)

    except common_functions.ApiException as e:

        print("Exception in RandoriApi->%s: %s\n" % (funct_name,e))

        sys.exit(1)

    for item in resp.data:

        print("#################\n#Sample JSON output for %s\n##################" % funct_name)

        print(item)

        print()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Compare File With Domains to Existing Domains in Platform')

    optional = parser._action_groups.pop()

    optional.add_argument("-e", "--endpoint", default=False,
        help="If the endpoint arg is provided, only show example output for the specified endpoint.")

    optional.add_argument ("-l", "--list_endpoints", action='store_true', default=False,
        help="If the list_endpoints argument is provided, print the available endpoints and exit.")

    parser._action_groups.append(optional)

    args = parser.parse_args()

    api_endpoints = ['get_all_detections_for_target', 'get_hostname', 'get_hostnames_for_ip',
                        'get_ip', 'get_ips_for_hostname', 'get_ips_for_network', 'get_ips_for_service', 
                        'get_network', 'get_ports_for_ip', 'get_service', 'get_target']

    
    if args.list_endpoints:

        print("Possible endpoints:\n%s" % api_endpoints)

        sys.exit(0)

    if args.endpoint:

        funct_name = args.endpoint

        get_sample_output(funct_name)

    else:
    
        for api_endpoint in api_endpoints:

            get_sample_output(api_endpoint)
        
