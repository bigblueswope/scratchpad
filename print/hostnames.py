import base64
import datetime
import json
import os
import sys

import common_functions
import entity_detector

#Initial Query:
#    Confidence Greater Than or Equal To 0
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
  }''')



if __name__ == '__main__':

    for host in common_functions.get_hostnames(initial_query):
        
        print(host.hostname, host.confidence)
                
