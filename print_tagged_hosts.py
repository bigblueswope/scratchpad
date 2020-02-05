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
      "field": "table.tags",
      "operator": "has_key",
      "value": ""
    }
  ],
  "valid": true
}''')



def prep_query(query_object):

   iq = json.dumps(query_object).encode()

   query = base64.b64encode(iq)

   return query



def iterate_hostnames(tag_string):
    more_targets_data= True
    offset = 0
    limit = 200
    sort = ['hostname']

    initial_query['rules'][0]['value'] = tag_string

    while more_targets_data:
        
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

        for item in resp.data:
            #print(item)
            print(item.tags[tag_string]['time_added'], '\t', item.hostname)
            #print(item.hostname, "\t\t", item.tags[tag_string]['time_added'])
            #print(item.hostname, item.confidence)
                


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Print Hostnames and Tag Details for hosts with the provided Tag')
    required = parser.add_argument_group('required arguments')
    required.add_argument("-t", "--tag", required=True, 
        help="Tag for which to search.  If tag includes spaces, enclose the string in quotes")

    args = parser.parse_args()

    iterate_hostnames(args.tag)
    
