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



def prep_query(query_object):

   iq = json.dumps(query_object).encode()

   query = base64.b64encode(iq)

   return query



def get_counts(endpoint, quiet):

    funct_name = 'get_' + endpoint

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

    if quiet:
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

    optional.add_argument ("-q", "--quiet", action='store_true', default=False,
        help="If quiet flag is given, do not print endpoint names, print just the counts.")
    parser._action_groups.append(optional)

    args = parser.parse_args()

    api_endpoints = [ 'target', 'service', 'hostname', 'ip', 'network']
    
    if args.list_endpoints:
        print("Possible endpoints:\n%s" % api_endpoints)
        sys.exit(0)

    if args.endpoint:
        get_counts(args.endpoint, args.quiet)

    else:
        for endpoint in api_endpoints:
            get_counts(endpoint, args.quiet)
        
