import argparse
import base64
import datetime
import json
import os
import pprint
import sys

import common_functions
import entity_detector

#Initial Query:
#    Confidence Greater Than or Equal To Medium
#    and
#    Target Temptation Greater Than or Equal To High
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.target_id",
      "operator": "equal",
      "value": "REPLACE_ME"
    }
  ],
  "valid": true
  }''')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Print the detections for a single target')

    required = parser.add_argument_group('required arguments')

    required.add_argument("-t", "--target_id", required=True, help="Target ID")

    args = parser.parse_args()

    initial_query['rules'][0]['value'] = args.target_id
    
    for detection in common_functions.get_all_detections_for_target(initial_query):
        print(detection, "\n#########################\n")
                

