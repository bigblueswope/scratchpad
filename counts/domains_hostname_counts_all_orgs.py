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

    header = ','.join(['Org', 'domain', 'platform_discovered', 'user_added'])

    print(header)

    for org_name in common_functions.get_orgs():

        common_functions.configuration.access_token = common_functions.get_api_token(org_name);

        prime_entity_domains = {}
        
        pes = get_platform_hosts()
    
        # POC is the first entity because the sort order for the query
        #  is first_seen and the POC is always the oldest entity
        #poc_ent = pes[0].hostname
    
        #print("POC:", poc_ent)
        
        for ent in pes:

            ent_type, ent_name, ent_dom = entity_detector.detect_entity(ent.hostname)

            if ent_type == 'domains':

                prime_entity_domains[ent_name] = {'platform_disc': 0, 'user_added':0}
            
            
            if ent_type == 'hostnames' and ent_dom in prime_entity_domains.keys():

                if ent.confidence == 100:

                    prime_entity_domains[ent_dom]['user_added'] += 1

                else:

                    prime_entity_domains[ent_dom]['platform_disc']  += 1
    
    
        #print(json.dumps(prime_entity_domains, indent=2))
        
        for k in prime_entity_domains.keys():

            foo = ','.join([org_name, k, str(prime_entity_domains[k]['platform_disc']), str(prime_entity_domains[k]['user_added'])])

            print(foo)
    
    
    
