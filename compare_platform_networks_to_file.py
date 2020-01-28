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
# Sample JSON returned by get_network
##########
'''
{'confidence': 25,
 'deleted': False,
 'first_seen': datetime.datetime(2018, 12, 3, 11, 2, 56, 488179, tzinfo=tzutc()),
 'id': 'cc912d03-5c43-4fc0-9bfd-0ca46258c828',
 'ip_count': 0,
 'last_seen': datetime.datetime(2020, 1, 19, 7, 52, 23, 89991, tzinfo=tzutc()),
 'max_confidence': 25,
 'network': '2001:1890:161c:8a00::/56',
 'network_str': '2001:1890:161c:8a00::/56',
 'open_port_count': 0,
 'org_id': '49be93a0-b5e4-4a47-b119-923972d590aa',
 'service_count': 0,
 'tags': {},
 'target_count': 0,
 'target_temptation': 0}
'''

def get_platform_networks():
    
    platform_networks = {}

    more_data= True
    offset = 0
    limit = 200
    sort = ['confidence']

    while more_data:
        
        query = prep_query(initial_query)

        try:
            resp = r_api.get_network(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_network: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_data = False
        else:
            offset = max_records

        for network in resp.data:
            #print(network)
            if not network.network in platform_networks.keys():
                platform_networks[network.network] = network.confidence

    return platform_networks

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Compare File With Networks to Existing Networks in Platform')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, help="File with possible additional networks")
    optional.add_argument("-o", "--output", default=False, 
        help="If the output arg/flag is provided, write missing networks to outfile.")
    parser._action_groups.append(optional)

    args = parser.parse_args()

    platform_networks = get_platform_networks()

    addl_networks= []
    both_networks = {}
    low_confidence_networks = {}

    with open(args.input, 'r+') as f:
        for line in f:
            new_network = line.rstrip('\n').rstrip(',')

            print('Network from file: ', new_network)

            if not new_network in platform_networks.keys():
                addl_networks.append(new_network)
            else :
                if platform_networks[new_network] < 60:
                    low_confidence_networks[new_network] = platform_networks[new_network]
                else:
                    both_networks[new_network] = platform_networks[new_network]
    
    print("\n###################\n")
    print("New Networks To Add To Platform:")

    for net in addl_networks:
        print(net)
    
    if args.output:
        with open(args.output, 'w+') as outfile:
            for net in addl_networks:
                outfile.write(net)
                outfile.write('\n')
            
    
    sys.stderr.write("\nCount of New Networks: %s\n" % str(len(addl_networks)))

    sys.stderr.write("\nMedium or Greater Confidence Networks in Platform and Input file: %s\n" % both_networks)

    sys.stderr.write("\nLow or Lesser Confidence Networks in Platform and Input file:%s\n" % low_confidence_networks)
    

