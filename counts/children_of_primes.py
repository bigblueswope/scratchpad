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
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
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

def get_platform_hosts():
    
    platform_hosts = []

    more_data= True
    offset = 0
    limit = 1000
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

        for host in resp.data:

            if not host.hostname in platform_hosts:

                platform_hosts.append(host)

    return platform_hosts



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Iterates all hosts for an org and separates into lists')

    optional = parser._action_groups.pop()

    parser._action_groups.append(optional)

    args = parser.parse_args()
    
    header = ','.join(['domain', 'platform_discovered', 'user_added'])

    print(header)

    for org_name in common_functions.get_orgs():

        common_functions.configuration.access_token = common_functions.get_api_token(org_name);

        #altering initial query to get prime entities
        initial_query['rules'][0]['value'] = 100
    
        prime_entity_domains = {}
        
        pes = get_platform_hosts()
    
        # POC is the first entity because the sort order for the query
        #  is first_seen and the POC is always the oldest entity
        #poc_ent = pes[0].hostname
    
        #print("POC:", poc_ent)
        
        for ent in pes:

            ent_type, ent_name, _ = entity_detector.detect_entity(ent.hostname)

            if ent_type == 'domains':

                prime_entity_domains[ent_name] = {'platform_disc': 0, 'user_added':0}
            
    
        #reverting initial query to get medium or higer entities
        initial_query['rules'][0]['value'] = 60
    
        platform_hosts = get_platform_hosts()
    
        for ent in platform_hosts:

            dom = entity_detector.get_domain(ent.hostname)
            
            if dom in prime_entity_domains.keys():

                if ent.confidence == 100:

                    prime_entity_domains[dom]['user_added'] += 1

                else:

                    prime_entity_domains[dom]['platform_disc']  += 1
    
    
        #print(json.dumps(prime_entity_domains, indent=2))
        
        for k in prime_entity_domains.keys():

            foo = ','.join([k, str(prime_entity_domains[k]['platform_disc']), str(prime_entity_domains[k]['user_added'])])

            print(foo)
    
    
    
