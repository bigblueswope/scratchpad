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
      "field": "table.hostname",
      "operator": "contains",
      "value": "REPLACEME"
    }
  ],
  "valid": true
}''')



if __name__ == '__main__':

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

            domain = common_functions.line_cleaner(line)
        
            initial_query['rules'][0]['value'] = domain
            
            for host in common_functions.get_hostnames(initial_query):
                
                if args.confidence:
                
                    print(host.hostname, host.confidence)
                
                else:
                    
                    print(host.hostname)
                
