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

ip_id_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.id",
      "operator": "equal",
      "value": "REPLACE_ME"
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

        #print(port)

        ip_id = port.ip_id

        ip_id_query['rules'][0]['value'] = ip_id

        result = common_functions.get_ips(ip_id_query)
        
        ip = result[0]

        print('Confidence:', ip.confidence, '\nFirst Seen:', ip.first_seen, '\nHostname:', ip.hostname, '\nID:', ip.id, '\nOpen Port Count:', ip.open_port_count)

'''
{'confidence': 75,
 'country': 'US',
 'deleted': False,
 'first_seen': datetime.datetime(2020, 2, 1, 1, 5, 0, 909619, tzinfo=tzutc()),
 'hostname': 'vmware.com',
 'hostname_count': 4,
 'id': '2fc54db9-240d-402a-a212-3dfcb558d460',
 'ip': '45.60.101.183',
 'ip_str': '45.60.101.183',
 'last_seen': datetime.datetime(2020, 5, 14, 0, 46, 10, 514928, tzinfo=tzutc()),
 'latitude': 37.751,
 'longitude': -97.822,
 'max_confidence': 75,
 'open_port_count': 51,
 'org_id': '410ab98b-0862-4ea8-b028-3a38ca96bd3d',
 'radius': None,
 'service_count': 4,
 'tags': {},
 'target_count': 4,
 'target_temptation': 27}
 '''
