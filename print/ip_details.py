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
      "field": "table.ip",
      "operator": "equal",
      "value": "REPLACE_ME"
    }
  ],
  "valid": true
}''')



if __name__ == '__main__':

    try:

        ip = sys.argv[1]
        
        initial_query['rules'][0]['value'] = ip

    except Exception as e:

        print(e)

        sys.exit(1)
    
    for ip in common_functions.get_ips(initial_query):

        print(ip)
                
