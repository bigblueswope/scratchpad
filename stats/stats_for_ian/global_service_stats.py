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



if __name__ == '__main__':

    all_org_services = {}

    for org_name in common_functions.get_orgs():

        common_functions.configuration.access_token = common_functions.get_api_token(org_name);

        for service in common_functions.get_services(initial_query):

            if service.service_id in all_org_services:

                all_org_services[service.service_id]['instance_count'] += service.instance_count

                all_org_services[service.service_id]['org_count'] += 1
                
            else:
                
                all_org_services[service.service_id] = {
                                                'applicability' : service.applicability,
                                                'criticality' : service.criticality,
                                                'enumerability' : service.enumerability,
                                                'instance_count' : service.instance_count,
                                                'name' : service.name,
                                                'org_count' : 1,
                                                'post_exploit' : service.post_exploit,
                                                'private_weakness' : service.private_weakness,
                                                'public_weakness' : service.public_weakness,
                                                'research' : service.research,
                                                'target_temptation' : service.target_temptation,
                                                'version' : service.version
                                                }
    
    header = ','.join(
        [
            'service_id',
            'service_name',
            'service_version',
            'target_temptation',
            'org_count',
            'instance_count',
            'applicability', 
            'criticality', 
            'enumerability',
            'post_exploit',
            'private_weakness',
            'public_weakness',
            'research'
        ]
    )
    
    td = datetime.datetime.today().strftime('%Y-%m-%d')

    filename = f'results/global_service_stats_{td}.csv'

    with open(filename, 'w') as file:
    
        file.write(header)
        file.write('\n')

        print(header)
        
        for k in all_org_services.keys():
    
            line = ','.join(
                [
                    k,
                    all_org_services[k]['name'],
                    str(all_org_services[k]['version']),
                    str(all_org_services[k]['target_temptation']),
                    str(all_org_services[k]['org_count']),
                    str(all_org_services[k]['instance_count']),
                    str(all_org_services[k]['applicability']),
                    str(all_org_services[k]['criticality']),
                    str(all_org_services[k]['enumerability']),
                    str(all_org_services[k]['post_exploit']),
                    str(all_org_services[k]['private_weakness']),
                    str(all_org_services[k]['public_weakness']),
                    str(all_org_services[k]['research'])
                ]
            )
            
            file.write(line)
            file.write('\n')

            print(line)

