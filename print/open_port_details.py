import base64
import datetime
import json
import os
import sys

import common_functions

#Initial Query:
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
      "value": "REPLACE_ME"
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

    except IndexError as e:

        print("Provide a port number as an argument.")

        sys.exit(1)

    if 'REPLACE_ME' in json.dumps(initial_query):

        print("'REPLACE_ME' found in the initial_query.  Invalid query.  Fix query and try again.")

        sys.exit(1)


    for port in common_functions.get_ports(initial_query):

        print(port)

