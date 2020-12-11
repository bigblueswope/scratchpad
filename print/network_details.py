import base64
import datetime
import json
import os
import sys

import common_functions
import entity_detector

initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": "REPLACE_ME"
    }
  ],
  "valid": true
}''')



if __name__ == '__main__':

    try:

        confidence = sys.argv[1]
        
        initial_query['rules'][0]['value'] = confidence

    except IndexError as e:

        print('Please provide a minimum confidence value')

        sys.exit(1)
    

    for network in common_functions.get_networks(initial_query):

        print(network)
                
