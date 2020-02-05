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
      "field": "table.hostname",
      "operator": "contains",
      "value": "REPLACEME"
    }
  ],
  "valid": true
}''')



def prep_query(query_object):

   iq = json.dumps(query_object).encode()

   query = base64.b64encode(iq)

   return query



def iterate_hostnames(domain):
    more_targets_data= True
    offset = 0
    limit = 200
    sort = ['hostname']

    while more_targets_data:
        
        initial_query['rules'][0]['value'] = domain

        query = prep_query(initial_query)

        try:
            resp = r_api.get_hostname(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_hostname: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_targets_data = False
        else:
            offset = max_records

        for hostname in resp.data:
            if args.confidence:
                print(hostname.hostname, hostname.confidence)
            else:
                print(hostname.hostname)
                


if __name__ == '__main__':

    path = '/Users/bj/.tokens/'

    parser = argparse.ArgumentParser(description = 'Print hostnames in Platform for Domain(s)')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, help="File with possible additional domains")
    optional.add_argument("-c", "--confidence", action='store_true', default=False,
        help="If provided, print confidence of the entity along with the entity name")
    parser._action_groups.append(optional)


    args = parser.parse_args()


    with open(args.input, 'r+') as f:
        for line in f:
            domain = line.rstrip('\n').rstrip(',')
            iterate_hostnames(domain)
    
