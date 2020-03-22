import base64
import datetime
import json
import os
from pathlib import Path
import sys

import common_functions
import entity_detector

#Initial Query:
#    Confidence Greater Than or Equal To Medium
#    and
#    Has Open Ports
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "field": "table.seen_open",
      "operator": "equal",
      "value": true
    }
  ],
  "valid": true
}
''')



##########
# Sample JSON returned by get_ports_for_ip
##########
'''
{'confidence': 75,
 'deleted': False,
 'id': 'fa65b758-1636-41d9-823e-b78c552aff62',
 'ip_id': '8c3e21b0-a6e7-4f46-bff9-2ed8575e7525',
 'last_seen': datetime.datetime(2019, 10, 7, 12, 25, 56, 107949, tzinfo=tzutc()),
 'max_confidence': 75,
 'org_id': '71803330-934a-4c4d-bd82-af1ba5e73ae8',
 'port': 443,
 'protocol': 6,
 'seen_open': True,
 'state': 'open'}
 '''


def iterate_ips_with_ports():
    more_targets_data= True
    offset = 0
    limit = 200
    sort = ['port']
    
    open_ports = {}
    
    while more_targets_data:
        
        query = common_functions.prep_query(initial_query)

        try:
            resp = common_functions.r_api.get_ports_for_ip(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except common_functions.ApiException as e:
            print("Exception in RandoriApi->get_target: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_targets_data = False
        else:
            offset = max_records

        for ip in resp.data:
            try:
                open_ports[ip.port] += 1
            except KeyError:
                open_ports[ip.port] = 1

        return open_ports

if __name__ == '__main__':
    ips_with_ports = iterate_ips_with_ports()
    
    for port, count in ips_with_ports.items():
        print(count, port)

