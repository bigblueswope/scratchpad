import base64
import datetime
import json
import os
import sys

import randori_api
from randori_api.rest import ApiException

from api_tokens import get_api_token, get_orgs


configuration = randori_api.Configuration()

org_name = os.getenv("RANDORI_ENV")

configuration.access_token = get_api_token(org_name);

configuration.host = "https://alpha.randori.io"

r_api = randori_api.RandoriApi(randori_api.ApiClient(configuration))




def line_cleaner(line):

    if ',' in line:
        #assumes domain/host is first entry in the CSV line
        line = line.split(',')[0]

    if '#' in line:
        # Treating # as an in-line comment so split on # for the first field
        line = line.split('#')[0]

    line = line.strip('*\n.,"\t ').lower()

    if line == 'domainname':
        # Skip empty line or line with value of "domainname"
        return None
    
    return line



def prep_query(query_object):

   iq = json.dumps(query_object).encode()

   query = base64.b64encode(iq)

   return query



def tt_to_string(tt):
    if tt >= 40:
        return 'Critical'
    elif tt >= 30:
        return 'High'
    elif tt >= 15:
        return 'Medium'
    else:
        return 'Low'




def get_hostnames(query):
    hostnames = []

    more_targets_data= True
    offset = 0
    limit = 1000
    sort = ['hostname']

    query = prep_query(query)

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


        for hostname in resp.data:

            hostnames.append(hostname)

    return hostnames




def get_ips(query):
    ips = []

    more_data= True
    offset = 0
    limit = 1000
    sort = ['ip']

    query = prep_query(query)

    while more_data:

        try:
            resp = r_api.get_ip(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_ip: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit

        if resp.total <= max_records:
            more_data = False
        else:
            offset = max_records

        for ip in resp.data:
            ips.append(ip)

    return ips



def get_port_details(initial_query):
    ips = []

    more_targets_data= True
    offset = 0
    limit = 1000
    sort = ['port']

    query = prep_query(initial_query)

    while more_targets_data:
        
        try:
            resp = r_api.get_ports_for_ip(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_target: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_targets_data = False
        else:
            offset = max_records

        for ip in resp.data:
            ips.append(ip)

    return ips
