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
    sort = ['hostname']

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

        for hostname in resp.data:
            if not hostname.hostname in platform_domains:
                platform_domains.append(hostname)

    return platform_domains

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Iterates all domains for an org and separates into lists')

    optional = parser._action_groups.pop()

    optional.add_argument("-v", "--verbose", default=False, action="store_true",
        help="If the verbose arg/flag is provided, print domains to std out.")

    optional.add_argument("-u", "--user_added", default=False, action="store_true",
        help="If the user arg/flag is provided, print user provided domains to std out.")

    optional.add_argument("-p", "--platform_discovered", default=False, action="store_true",
        help="If the platform discovered arg/flag is provided, print platform discovered domains to std out.")

    parser._action_groups.append(optional)

    args = parser.parse_args()

    platform_domains = get_platform_domains()

    discovered_domains = []
    user_domains = []

    for domain in platform_domains:
        if domain.confidence == 100:
            user_domains.append(domain.hostname)
        else:
            discovered_domains.append(domain.hostname)
    
    if args.verbose:
        print("Platform Discovered Domains: %s" % discovered_domains)
        print()
        print("User Added Domains: %s" % user_domains)

    if args.user_added:
        print("User Added Domains: %s" % user_domains)

    if args.platform_discovered:
        print("Platform Discovered Domains: %s" % discovered_domains)
    
    sys.stderr.write("\nCount of Discovered Domains: %s\n" % str(len(discovered_domains)))

    sys.stderr.write("\nCount of User Added Domains: %s\n" % str(len(user_domains)))
    
