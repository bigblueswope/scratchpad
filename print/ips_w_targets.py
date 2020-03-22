import base64
import datetime
import json
import os
import sys

import common_functions
import entity_detector

#Initial Query:
#    Confidence Greater Than or Equal To Medium
#    and
#    Target Temptation Greater Than or Equal To 1
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "condition": "AND",
      "rules": [
        {
          "field": "table.target_temptation",
          "operator": "greater_or_equal",
          "value": 1
        }
      ]
    }
  ],
  "valid": true
}''')


if __name__ == '__main__':

    for ip in common_functions.get_ips(initial_query):
        print(ip)
    
