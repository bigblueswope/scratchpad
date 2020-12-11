import argparse
import base64
import json
import os
import sys

import common_functions
import entity_detector


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




def get_platform_networks():
    
    platform_networks = {}

    more_data= True
    offset = 0
    limit = 200
    sort = ['network']

    while more_data:
        
        query = common_functions.prep_query(initial_query)

        try:
            resp = common_functions.r_api.get_network(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except common_functions.ApiException as e:
            print("Exception in RandoriApi->get_network: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_data = False
        else:
            offset = max_records

        for network in resp.data:
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
    non_networks = []
    src_duplicates = 0

    with open(args.input, 'r+') as f:

        for line in f:
        
            new_network = common_functions.line_cleaner(line)

            if not new_network:
                continue

            ent_type, _, _ = entity_detector.detect_entity(new_network)

            if not ent_type == 'networks':
                non_networks.append(new_network)
                continue


            if not new_network in platform_networks.keys() and not new_network in addl_networks:
                addl_networks.append(new_network)
            else :
                try:
                    if platform_networks[new_network] < 60:
                        low_confidence_networks[new_network] = platform_networks[new_network]
                    else:
                        try:
                            both_networks[new_network] = platform_networks[new_network]
                        except KeyError:
                            # network is a dupe from the source file
                            src_duplicates += 1
                            continue
                except KeyError:
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
    
    sys.stderr.write("\nNon-Network entities in input file: %s\n" % non_networks)


