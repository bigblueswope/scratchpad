import argparse
import base64
import json
import os
import sys

import randori_api
from randori_api.rest import ApiException

configuration = randori_api.Configuration()

configuration.access_token = os.getenv("RANDORI_API_KEY");

configuration.host = "https://alpha.randori.io"

r_api = randori_api.RandoriApi(randori_api.ApiClient(configuration))


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



def prep_query(query_object):

   iq = json.dumps(query_object).encode()

   query = base64.b64encode(iq)

   return query



def get_sample_output(funct_name):
    offset = 0
    limit = 1
    sort = ['confidence']

    query = prep_query(initial_query)

    
    try:
        da_funct = getattr(r_api, funct_name)

        resp = da_funct(offset=offset, limit=limit,
                                sort=sort, q=query)
    except ApiException as e:
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

    api_endpoints = ['detection_target', 'detections_for_target', 'hostname', 'hostnames_for_ip',
                        'ips_for_hostname', 'ips_for_network', 'ips_for_service', 'network',
                        'ports_for_ip', 'service', 'target']

    
    if args.list_endpoints:
        print("Possible endpoints:\n%s" % api_endpoints)
        sys.exit(0)

    if args.endpoint:
        funct_name = 'get_' + args.endpoint
        get_sample_output(funct_name)

    else:
    
        for api_endpoint in api_endpoints:
            funct_name = 'get_' + api_endpoint
            get_sample_output(funct_name)
        
