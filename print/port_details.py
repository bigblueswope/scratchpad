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
#    Port # and Port is open

initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "field": "table.port",
      "operator": "equal",
      "value": "REPLACE.ME"
    },
    {
      "field": "table.state",
      "operator": "equal",
      "value": "open"
    }
  ],
  "valid": true
  }''')



if __name__ == '__main__':
    try:

        port = sys.argv[1]

        initial_query['rules'][1]['value'] = port

    except IndexError:

        print('Script requires a single argument, port number. Rerun script with port specified.')

        sys.exit(1)


    for ip in common_functions.get_port_details(initial_query):
        print(ip)



