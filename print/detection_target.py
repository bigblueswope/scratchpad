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



def get_detection_targets(initial_query):
    detections = []

    more_targets_data= True
    offset = 0
    limit = 1000
    sort = ['hostname']

    query = common_functions.prep_query(initial_query)

    while more_targets_data:
        
        try:
            resp = common_functions.r_api.get_detection_target(offset=offset, limit=limit,
                                    sort=sort, q=query)

        except common_functions.ApiException as e:

            print("Exception in RandoriApi->get_target: %s\n" % e)

            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:

            more_targets_data = False

        else:

            offset = max_records
        
        return resp.data


if __name__ == '__main__':
    
    for detection_target in get_detection_targets(initial_query):
        print(detection_target, "\n")
                

