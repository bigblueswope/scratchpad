import argparse
import base64
import json
import os
import sys

import common_functions
import entity_detector

list_of_ports = []
    
with open('sources/randori_scanned_ports_sorted.txt', 'r') as f:

    for line in f: 
        
        line = line.strip() 
        
        list_of_ports.append(line) 


with open('vertical_lists/hc_orgs.json') as f:
  orgs = json.load(f)['orgs']



#Initial Query:
medium_conf_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "field": "table.state",
      "operator": "equal",
      "value": "open"
    }
  ],
  "valid": true
}''')



if __name__ == '__main__':

    all_org_ports = []

    for org_name in common_functions.get_orgs():
    #for org_name in ['webernets-alpha', 'schonfeld']:
        
        #print(org_name)

        common_functions.configuration.access_token = common_functions.get_api_token(org_name)


        port_counts = {'org_id': ''}

        for p in list_of_ports:
            port_counts[p] = 0
        
        org_ports = common_functions.get_ports(medium_conf_query)
        
        if not org_ports[0].org_id in orgs:
            continue

        port_counts['org_id'] = org_ports[0].org_id

        for result in org_ports:
            port_counts[str(result.port)] +=1
        
        all_org_ports.append(port_counts.copy())

    header = ','.join(all_org_ports[0].keys())

    print(header)

    for each_org in all_org_ports:

        temp_list = []
        
        for value in each_org.values():

            temp_list.append(str(value))

        line = ','.join(temp_list) 

        print(line)
    
