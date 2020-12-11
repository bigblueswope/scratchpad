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
      "condition": "OR",
      "rules": [
        {
          "condition": "AND",
          "label": "medium",
          "rules": [
            {
              "field": "table.confidence",
              "id": "table.confidence",
              "input": "number",
              "operator": "greater_or_equal",
              "type": "integer",
              "value": 26
            },
            {
              "field": "table.confidence",
              "id": "table.confidence",
              "input": "number",
              "operator": "less_or_equal",
              "type": "integer",
              "value": 74
            }
          ]
        },
        {
          "condition": "AND",
          "label": "high",
          "rules": [
            {
              "field": "table.confidence",
              "id": "table.confidence",
              "input": "number",
              "operator": "greater_or_equal",
              "type": "integer",
              "value": 75
            },
            {
              "field": "table.confidence",
              "id": "table.confidence",
              "input": "number",
              "operator": "less_or_equal",
              "type": "integer",
              "value": 100
            }
          ]
        }
      ],
      "ui_id": "confidence"
    }
  ]
}''')



if __name__ == '__main__':

    for service in common_functions.get_services(initial_query):
        
        print(service)
        print("####################\n")

        #print(target.hostname, target.confidence)
                
