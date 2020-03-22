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
      "field": "table.tags",
      "operator": "contains",
      "type": "string",
      "value": []
    }
  ],
  "valid": true
}''')





if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Print Hostnames and Tag Details for hosts with the provided Tag')

    required = parser.add_argument_group('required arguments')

    required.add_argument("-t", "--tag", required=True, 
        help="Tag for which to search.  If tag includes spaces, enclose the string in quotes")

    args = parser.parse_args()

    initial_query['rules'][0]['value'].append(args.tag)

    for host in common_functions.get_hostnames(initial_query):
        print(host)
    
