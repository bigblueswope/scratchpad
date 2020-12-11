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
      "field": "table.target_temptation",
      "operator": "greater_or_equal",
      "value": 20
    }
  ],
  "valid": true
  }''')



if __name__ == '__main__':

    common_functions.print_raw_targets(initial_query)
        
                
