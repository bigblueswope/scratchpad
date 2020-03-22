import base64
import datetime
import json
import os
import sys

import common_functions


#Initial Query:
#    Confidence Greater Than or Equal To Zero
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 0
    }
  ],
  "valid": true
  }''')


##########
# Sample JSON returned by get_hostname
##########
'''
{'confidence': 75,
 'deleted': False,
 'first_seen': datetime.datetime(2019, 9, 13, 20, 18, 45, 334601, tzinfo=tzutc()),
 'hostname': 'www.webernets.online',
 'id': 'bc6a641f-eef5-444f-9311-1d43da55638c',
 'ip_count': 15,
 'last_seen': datetime.datetime(2019, 10, 7, 12, 25, 56, 107949, tzinfo=tzutc()),
 'max_confidence': 75,
 'name_type': 1,
 'org_id': '71803330-934a-4c4d-bd82-af1ba5e73ae8',
 'tags': {},
 'target_temptation': 22}
 '''

def iterate_hostnames():
    more_targets_data= True
    offset = 0
    limit = 200
    sort = ['hostname']

    hostnames_dict = {}

    while more_targets_data:
        
        query = common_functions.prep_query(initial_query)

        try:
            resp = common_functions.r_api.get_hostname(
                        offset=offset, limit=limit,
                        sort=sort, q=query)

        except common_functions.ApiException as e:
            print("Exception in RandoriApi->get_target: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_targets_data = False
        else:
            offset = max_records
        
        
        for hostname in resp.data:

            print(hostname.hostname)

            try:
                hostnames_dict[hostname.hostname] += 1
            except KeyError:
                hostnames_dict[hostname.hostname] = 1

                
    
    for k,v in hostnames_dict.items():
        if v > 1:
            print("Duplicate hostname found: %s" % k)

if __name__ == '__main__':
    iterate_hostnames()
    
