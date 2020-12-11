import argparse
import base64
import datetime
import json
import os
import sys

import common_functions
import entity_detector

import randori_api
from randori_api.rest import ApiException

from api_tokens import get_api_token, get_orgs


configuration = randori_api.Configuration()

configuration.host = "https://alpha.randori.io"

r_api = randori_api.DefaultApi(randori_api.ApiClient(configuration))


#Initial Query:
#    Confidence Greater Than or Equal To Medium
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 25
    },
    {
      "field": "table.confidence",
      "operator": "less",
      "value": 60
    }
  ],
  "valid": true
}''')


def get_hosts(query):
    hosts = []

    more_targets_data = True
    offset = 0
    limit = 1000
    sort = ['first_seen']

    query = common_functions.prep_query(query)

    while more_targets_data:

        try:
            resp = r_api.get_hostname(offset=offset, limit=limit,
                                    sort=sort, q=query)

        except ApiException as e:

            print("Exception in RandoriApi->get_hostname: %s\n" % e)

            sys.exit(1)

        max_records = offset + limit

        if resp.total <= max_records:

            more_targets_data = False

        else:

            offset = max_records

        for host in resp.data:

            hosts.append(host)

    return hosts



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Iterates all hosts for an org and separates into lists')

    print(','.join(['org_name', 'low_confidence_domains', 'low_confidence_hostnames']))

    #for org_name in ['webernets-alpha', 'enterpriseproducts']:
    for org_name in common_functions.get_orgs():
        
        both_low_confidence_types = {}

        low_confidence_entity_domains = {}
        
        low_confidence_entity_hostnames = {}
        
        configuration.access_token = get_api_token(org_name)
        
        # retrieves entities with 100 confidence
        pes = get_hosts(initial_query)
    
        for ent in pes:
    
            ent_type, ent_name, _ = entity_detector.detect_entity(ent.hostname)
    
            if ent_type == 'domains':
    
                low_confidence_entity_domains[ent_name] = ent.first_seen.strftime("%Y-%m-%d %H:%M:%S")

            else:
                
                low_confidence_entity_hostnames[ent_name] = ent.first_seen.strftime("%Y-%m-%d %H:%M:%S")
    
        
        both_low_confidence_types['domains'] = low_confidence_entity_domains.copy()

        both_low_confidence_types['hostnames'] = low_confidence_entity_hostnames.copy()
        
        print(','.join([org_name, str(len(low_confidence_entity_domains)), str(len(low_confidence_entity_hostnames))]))

        with open(f'output/{org_name}_low_confidence_entities.json', 'w') as f:
            
            print(both_low_confidence_types)
            
            f.write(json.dumps(both_low_confidence_types, indent = 4))

