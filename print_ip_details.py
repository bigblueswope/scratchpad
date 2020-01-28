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

import randori_api
from randori_api.rest import ApiException

import shodan

configuration = randori_api.Configuration()

configuration.access_token = os.getenv("RANDORI_API_KEY")

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

configuration.host = "https://alpha.randori.io"

r_api = randori_api.RandoriApi(randori_api.ApiClient(configuration))

initial_query = json.loads('''{
   "condition": "AND",
  "rules": [
    {
      "field": "table.ip",
      "operator": "equal",
      "value": "xxxx"
    }
  ],
  "valid": true
}''')


def prep_query(query_object):

   iq = json.dumps(query_object).encode()

   query = base64.b64encode(iq)

   return query



def tt_to_string(tt):
    if tt >= 40:
        return 'Critical'
    elif tt >= 30:
        return 'High'
    elif tt >= 15:
        return 'Medium'
    else:
        return 'Low'

##########
# Sample JSON returned by get_hostname
##########
'''
 
'''

def get_ip_info(input_ip):
    more_targets_data= True
    offset = 0
    limit = 200
    sort = ['hostname']

    while more_targets_data:
        
        initial_query['rules'][0]['value'] = input_ip

        query = prep_query(initial_query)

        try:
            resp = r_api.get_ip(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_target: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_targets_data = False
        else:
            offset = max_records

        for ip in resp.data:
            print(ip)
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Print the details about an IP Address')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, help="IP Address to Lookup")

    args = parser.parse_args()

    input_ip = args.input
    
    get_ip_info(input_ip)
