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
      "field": "table.open_port_count",
      "operator": "greater_or_equal",
      "value": 50
    }
  ],
  "valid": true
}''')


if __name__ == '__main__':

    for org in common_functions.get_orgs():

        print("Processing Org: %s" % org)

        common_functions.configuration.access_token = common_functions.get_api_token(org);

        for ip in common_functions.get_ips(initial_query):
            print(ip)
        
    
