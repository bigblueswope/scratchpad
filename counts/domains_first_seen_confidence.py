import argparse
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
#    Name Type Equal 0 (i.e. domains instead of hosts)
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "field": "table.name_type",
      "operator": "equal",
      "value": 0
    }
  ],
  "valid": true
}''')


##########
# Sample JSON returned by get_hostname
##########
'''
{'confidence': 100,
 'deleted': False,
 'first_seen': datetime.datetime(2019, 12, 3, 15, 4, 42, 791147, tzinfo=tzutc()),
 'hostname': 'adomainname.com',
 'id': '675c5c33-c1ec-4b5d-a888-b99e5b1527de',
 'ip_count': 1,
 'last_seen': datetime.datetime(2019, 12, 10, 6, 48, 21, 163969, tzinfo=tzutc()),
 'max_confidence': 100,
 'name_type': 0,
 'org_id': '3cf5a2db-d863-43eb-b08e-a15816d70062',
 'tags': {'User Provided': {'content': 'User Provided',
                            'display': True,
                            'hostname_uuid': '675c5c33-c1ec-4b5d-a888-b99e5b1527de',
                            'time_added': '2019-12-03T15:04:42.830842+00:00',
                            'user_id': '16c5a6d7-92c4-4207-9535-dd11f94432b7'}},
 'target_temptation': 0}
 '''

def get_platform_domains():
    
    platform_domains = []

    more_data= True
    offset = 0
    limit = 200
    sort = ['first_seen']

    while more_data:
        
        query = common_functions.prep_query(initial_query)

        try:
            resp = common_functions.r_api.get_hostname(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except common_functions.ApiException as e:
            print("Exception in RandoriApi->get_hostname: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_data = False
        else:
            offset = max_records

        for entity in resp.data:
            if not entity.hostname in platform_domains:
                platform_domains.append(entity)

    return platform_domains

if __name__ == '__main__':

    discovered_domains = []
    user_domains = []
    user_hostnames = []

    entities = get_platform_domains()

    for entity in entities:
        
        entity_type,_,_ = entity_detector.detect_entity(entity.hostname)
        
        if entity_type == 'domains' and entity.confidence == 100:
            
            user_domains.append({entity.hostname: f'{entity.first_seen},{entity.confidence}'})
            
        elif entity_type == 'domains':
            
            discovered_domains.append({entity.hostname: f'{entity.first_seen},{entity.confidence}'})

        else:

            user_hostnames.append({entity.hostname: f'{entity.first_seen},{entity.confidence}'})
    
    
    print(("#"*80))
    print('Platform Discovered Domains')
    print(("#"*80))

    for dom in discovered_domains:
        
        for k,v in dom.items():
            print(f'{k},{v}')
    
    print()
    
    print(("#"*80))
    print('Manually Added Domains')
    print(("#"*80))

    for dom in user_domains:
        for k,v in dom.items():
            print(f'{k},{v}')

    print()
    
    print(("#"*80))
    print('Manually Added Hostnames')
    print(("#"*80))

    for dom in user_hostnames:
        for k,v in dom.items():
            print(f'{k},{v}')

    sys.stderr.write("\nCount of Discovered Domains: %s\n" % str(len(discovered_domains)))

    sys.stderr.write("\nCount of User Added Domains: %s\n" % str(len(user_domains)))
    
    sys.stderr.write("\nCount of User Added Hostnames: %s\n" % str(len(user_hostnames)))
    
