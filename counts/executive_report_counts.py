import argparse
import base64
import copy
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

# Port Rule:
#   Port is Open
port_rule = json.loads('''
{
    "field": "table.state",
    "operator": "equal",
    "value": "open"
}
''')



def get_service_count():

    offset = 0
    limit = 1
    sort = ['target_temptation']
    query = common_functions.prep_query(initial_query)
    
    try:

        resp = common_functions.r_api.get_service(offset=offset, limit=limit, sort=sort, q=query)
    
    except common_functions.ApiException as e:

        print("Exception in RandoriApi->get_service: %s\n" % e)

        sys.exit(1)
        
    return resp.total



def get_port_count():

    port_query = copy.deepcopy(initial_query)

    port_query['rules'].append(port_rule)
    
    offset = 0
    limit = 1
    sort = []
    query = common_functions.prep_query(port_query)
    
    try:

        resp = common_functions.r_api.get_ports_for_ip(offset=offset, limit=limit, sort=sort, q=query)
    
    except common_functions.ApiException as e:

        print("Exception in RandoriApi->get_ports_for_ip: %s\n" % e)

        sys.exit(1)
        
    return resp.total



def get_ip_count():

    offset = 0
    limit = 1
    sort = []
    query = common_functions.prep_query(initial_query)
    
    try:

        resp = common_functions.r_api.get_ip(offset=offset, limit=limit, sort=sort, q=query)
    
    except common_functions.ApiException as e:

        print("Exception in RandoriApi->get_ip: %s\n" % e)

        sys.exit(1)
        
    return resp.total



def get_hostname_count():

    offset = 0
    limit = 1
    sort = []
    query = common_functions.prep_query(initial_query)
    
    try:

        resp = common_functions.r_api.get_hostname(offset=offset, limit=limit, sort=sort, q=query)
    
    except common_functions.ApiException as e:

        print("Exception in RandoriApi->get_hostname: %s\n" % e)

        sys.exit(1)
        
    return resp.total



def get_top_16_tt_hostnames():
    
    top_16 = []

    offset = 0
    limit = 16
    sort = ['-priority_score', 'hostname']
    query = common_functions.prep_query(initial_query)

    try:

        resp = common_functions.r_api.get_hostname(offset=offset, limit=limit, sort=sort, q=query)

    except common_functions.ApiException as e:

        print("Exception in RandoriApi->get_hostname: %s\n" % e)

        sys.exit(1)

    for hn in resp.data:
        top_16.append(hn.hostname)

    return top_16


def get_top_3_tt_services():

    top_3_services = []

    offset = 0
    limit = 3
    sort = ['-target_temptation']
    query = common_functions.prep_query(initial_query)

    try:

        resp = common_functions.r_api.get_service(offset=offset, limit=limit, sort=sort, q=query)

    except common_functions.ApiException as e:

        print("Exception in RandoriApi->get_service: %s\n" % e)

        sys.exit(1)

    for svc in  resp.data:
        
        svc_and_version = svc.name + ' ' + svc.version
        
        top_3_services.append(svc_and_version)

    return top_3_services



if __name__ == '__main__':

    print('')

    host_count = get_hostname_count()

    print(f'Hostname Count: {host_count:,}')

    ip_count = get_ip_count()

    print(f'IP Count: {ip_count:,}')

    port_count = get_port_count()
    
    print(f'Open Port Count: {port_count:,}')
    
    service_count = get_service_count()

    print(f'Service Count: {service_count:,}')

    top_16_tt_hostnames = get_top_16_tt_hostnames()
    
    print('\nTop 16 Hostnames:')

    for hn in top_16_tt_hostnames:
        print(hn)

    top_3_tt_svcs = get_top_3_tt_services()

    print('\nTop 3 Services:')

    for sv in top_3_tt_svcs:
        print(sv)
