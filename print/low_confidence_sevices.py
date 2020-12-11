import base64
import datetime
import json
import os
import sys

import common_functions
import entity_detector

import randori_api

configuration = randori_api.Configuration()


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
          "rules": [
            {
              "field": "table.confidence",
              "operator": "greater_or_equal",
              "value": 26
            },
            {
              "field": "table.confidence",
              "operator": "less_or_equal",
              "value": 60
            }
          ]
        }
      ]
    }
  ]
}''')



if __name__ == '__main__':

    for org in common_functions.get_orgs():

        print('Processing {}'.format(org))

        configuration.access_token = common_functions.get_api_token(org)

        for service in common_functions.get_services(initial_query):
        
            print(service)
                
