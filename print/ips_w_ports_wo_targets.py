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
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "field": "table.open_port_count",
      "operator": "greater",
      "value": 0
    },
    {
      "field": "table.target_count",
      "operator": "equal",
      "value": 0
    }
  ],
  "valid": true
}''')



if __name__ == '__main__':
    for ip in common_functions.get_ips(initial_query):
        print(ip)
    
