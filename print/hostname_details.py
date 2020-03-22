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
      "field": "table.hostname",
      "operator": "equal",
      "value": "REPLACE_ME"
    }
  ],
  "valid": true
}''')


if __name__ == '__main__':
    try:
        hn = sys.argv[1]
    except IndexError as e:
        print("Must provide 1 hostname as the first argument when running the script.  Run again.")
        sys.exit(1)

    initial_query['rules'][0]['value'] = hn

    try:

        for host in common_functions.get_hostnames(initial_query):

            print(host)

    except Exception as e:

        print(e)
 


