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
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    }
  ],
  "valid": true
  }''')



if __name__ == '__main__':
    
    for detection_target in common_functions.get_all_detections_for_target(initial_query):
        print(detection_target, "\n")
                

