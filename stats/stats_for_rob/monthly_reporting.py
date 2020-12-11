import argparse
import base64
import datetime
import json
import os
import sys

import common_functions
import entity_detector

#Initial Query:

specific_targets_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "field": "table.target_temptation",
      "operator": "greater_or_equal",
      "value": ""
    },
    {
  "field": "table.target_temptation",
  "operator": "less",
  "value": ""
}
  ],
  "valid": true
}''')


medium_conf_query = json.loads('''{
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



def query_for_targets(lower, upper):

    offset = 0

    limit = 1

    sort = ['-target_temptation']

    specific_targets_query['rules'][1]['value'] = lower

    specific_targets_query['rules'][2]['value'] = upper
    
    query = common_functions.prep_query(specific_targets_query)
    
    try:

        resp = common_functions.r_api.get_target(offset=offset, limit=limit,
                                sort=sort, q=query)
    
    except common_functions.ApiException as e:

        print("Exception in RandoriApi->get_target: %s\n" % e)

        sys.exit(1)
    
    try:
        org_id = resp.data[0].org_id
    except IndexError as e:
        org_id = ''

    target_count = resp.total
    
    return(org_id, target_count)






def query_for_services():
    offset = 0

    limit = 1

    sort = ['-confidence']
    
    query = common_functions.prep_query(medium_conf_query)
    
    try:

        resp = common_functions.r_api.get_service(offset=offset, limit=limit,
                                sort=sort, q=query)

    except common_functions.ApiException as e:

        print("Exception in RandoriApi->get_service: %s\n" % e)

        sys.exit(1)

    org_id = resp.data[0].org_id

    service_total = resp.total

    return(org_id, service_total)



def query_for_ips():
    offset = 0

    limit = 1

    sort = ['-confidence']
    
    query = common_functions.prep_query(medium_conf_query)
    
    try:

        resp = common_functions.r_api.get_ip(offset=offset, limit=limit,
                                sort=sort, q=query)

    except common_functions.ApiException as e:

        print("Exception in RandoriApi->get_ip: %s\n" % e)

        sys.exit(1)

    org_id = resp.data[0].org_id

    ip_total = resp.total

    return(org_id, ip_total)



def query_for_networks():
    offset = 0

    limit = 1

    sort = ['-confidence']

    query = common_functions.prep_query(medium_conf_query)

    try:

        resp = common_functions.r_api.get_network(offset=offset, limit=limit,
                                sort=sort, q=query)

    except common_functions.ApiException as e:

        print("Exception in RandoriApi->get_network: %s\n" % e)

        sys.exit(1)

    network_total = resp.total

    return network_total



def query_for_ports():
    offset = 0
    limit = 1
    sort = ['-confidence']

    query = common_functions.prep_query(medium_conf_query)

    try:
        resp = common_functions.r_api.get_ports_for_ip(offset=offset, limit=limit,
                                      sort=sort, q=query) 
    except common_functions.ApiException as e:
        print("Exception in RandoriApi->get_ports_for_ip: %s\n" % e)
        sys.exit(1)

    print(resp)




if __name__ == '__main__':

    all_org_services = []

    #for org_name in common_functions.get_orgs():
    for org_name in ['webernets-alpha', 'schonfeld']:
        
        print(org_name)

        common_functions.configuration.access_token = common_functions.get_api_token(org_name)

        now = datetime.datetime.now()

        results = { 'org_id': '', 
                    'entity_type': '',
                    'affiliation_state_unset': 0,
                    'affiliation_state_set': 0,
                    'authorization_state_unset': 0
                    'authorization_state_set': 0,
                    'confidence_max': 0,
                    'confidence_crit': 0,
                    'confidence_high': 0,
                    'confidence_med': 0,
                    'confidence_low': 0,
                    'impact_score_none': 0,
                    'impact_score_low': 0,
                    'impact_score_med': 0,
                    'impact_score_high':0,
                    'perspective_public': 0,
                    'perspective_internal': 0,
                    'priority_score_low': 0,
                    'priority_score_med': 0,
                    'priority_score_high': 0,
                    'status_none': 0,
                    'status_accepted': 0,
                    'status_mitigated': 0,
                    'status_needs_review': 0,
                    'status_needs_resolution': 0,
                    'status_needs_investigation': 0,
                    'target_tempation_low': 0,
                    'target_temptation_med': 0,
                    'target_temptation_high': 0,
                    'target_temptation_crit': 0,
                    'timestamp': now
                    }
        
        # Count Targets
        for t_range in [ (0, 101, 'all_targets'), 
                       (0, 15, 'low_targets'), 
                       (15, 30, 'medium_targets'), 
                       (30, 40, 'high_targets'), 
                       (40, 101, 'critical_targets')]:

            org_id, target_count = query_for_targets(t_range[0], t_range[1])

            if results['org_id'] == '':
                results['org_id'] = org_id

            results[t_range[2]] = target_count


        #Count Services
        org_id, service_count = query_for_services()
        results['service_count'] = service_count

        
        #Count IPs
        org_id, ip_count = query_for_ips()
        results['ip_count'] = ip_count
        
        
        #Count Networks
        network_count = query_for_networks()
        results['network_count'] = network_count
        

        all_org_services.append(results.copy())

    td = datetime.datetime.today().strftime('%Y-%m-%d')

    filename = f'results/global_target_stats_{td}.csv'

    with open(filename, 'w') as file:

        header = ','.join(all_org_services[0].keys())
        
        file.write(header)
        file.write('\n')

        print(header)
    
    
        for each_org in all_org_services:
            temp_list = []
            
            for value in each_org.values():
                temp_list.append(str(value))
    
            line = ','.join(temp_list) 

            file.write(line)
            file.write('\n')

            print(line)
