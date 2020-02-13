import argparse
import base64
import json
import os
import sys

import randori_api
from randori_api.rest import ApiException

from keys.api_tokens import get_api_token

configuration = randori_api.Configuration()

org_name = os.getenv("RANDORI_ENV")

configuration.access_token = get_api_token(org_name);
#configuration.access_token = os.getenv("RANDORI_API_KEY");

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
}
''')



def prep_query(query_object):

   iq = json.dumps(query_object).encode()

   query = base64.b64encode(iq)

   return query



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
    required.add_argument("-i", "--input", required=True, 
        help="File with possible additional networks")
    optional.add_argument("-o", "--output", default=False, 
        help="If the output arg/flag is provided, write missing networks to outfile.")
    parser._action_groups.append(optional)

    args = parser.parse_args()

    platform_networks = get_platform_networks()

    addl_networks= []
    both_networks = {}
    low_confidence_networks = {}
    src_duplicates = 0

    with open(args.input, 'r+') as f:
        for line in f:
            new_network = line.rstrip('\n').rstrip(',')

            if not new_network in platform_networks.keys() and not new_network in addl_networks:
                addl_networks.append(new_network)
            else :
                if platform_networks[new_network] < 60:
                    low_confidence_networks[new_network] = platform_networks[new_network]
                else:
                    try:
                        both_networks[new_network] = platform_networks[new_network]
                    except KeyError:
                        # network is a dupe from the source file
                        src_duplicates += 1
                        continue
    
    print("\n###################\n")
    print("New Networks To Add To Platform:")

    for net in addl_networks:
        print(net)
    
    if args.output:
        with open(args.output, 'w+') as outfile:
            for net in addl_networks:
                outfile.write(net)
                outfile.write('\n')
            
    
    sys.stderr.write("\nCount of New Networks: %i\n" % len(addl_networks))

    sys.stderr.write("\nCount of duplicates in source file: %i\n" % src_duplicates)

    sys.stderr.write("\nMedium or Greater Confidence Networks in Platform and Input file: %s\n" % both_networks)

    sys.stderr.write("\nLow or Lesser Confidence Networks in Platform and Input file:%s\n" % low_confidence_networks)
    

