from copy import copy
from time import sleep
import base64
import http.client
import json
import os
import socket
import ssl
import sys


import randori_api
from randori_api.rest import ApiException

from keys.api_tokens import get_api_token

configuration = randori_api.Configuration()

org_name = os.getenv("RANDORI_ENV")

configuration.access_token = get_api_token(org_name);
#configuration.access_token = os.getenv("RANDORI_API_KEY");

configuration.host = "https://alpha.randori.io"

r_api = randori_api.RandoriApi(randori_api.ApiClient(configuration))




def prep_query(query_object):
   iq = json.dumps(query_object).encode()
   query = base64.b64encode(iq)
   return query




internal_tags_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "field": "table.tags",
      "id": "table.tags",
      "input": "text",
      "operator": "has_key",
      "type": "string",
      "ui_id": "tags",
      "value": "INTERESTING+Internal"
    }
  ]
}''')

def count_internal_hosts():
    
    more_targets_data= True
    offset = 0
    limit = 1
    sort = ['hostname']

    while more_targets_data:

        query = prep_query(internal_tags_query)

        try:
            resp = r_api.get_hostname(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in function count_internal_hosts calling RandoriApi->get_hostname: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        more_targets_data = False

        return resp.total
        

def count_internal_ips():
    
    more_targets_data= True
    offset = 0
    limit = 1
    sort = ['hostname']

    while more_targets_data:

        query = prep_query(internal_tags_query)

        try:
            resp = r_api.get_ip(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in function count_internal_ips calling RandoriApi->get_hostnames_for_ip: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        more_targets_data = False

        return resp.total
        

ports_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "field": "table.port",
      "operator": "equal",
      "value": ""
    },
    {
      "field": "table.state",
      "operator": "equal",
      "value": "open"
    }
  ],
  "valid": true
  }''')


def count_ips_with_ports(port):

    more_targets_data= True
    offset = 0
    limit = 1
    sort = ['port']

    ports_query['rules'][1]['value'] = port
    
    query = prep_query(ports_query)

    while more_targets_data:
        try:
            resp = r_api.get_ports_for_ip(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in function count_ips_with_ports calling RandoriApi->get_ports_for_ip: %s\n" % e)
            sys.exit(1)
        
        more_targets_data = False

    return resp.total


four_or_five_pub_weakness_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "field": "table.public_weakness",
      "operator": "greater_or_equal",
      "value": 4
    }
  ],
  "valid": true
 }''')


def count_four_or_five_pub_weaknesses():
    
    more_targets_data = True
    offset = 0
    limit = 1
    sort = ['public_weakness']

    query = prep_query(four_or_five_pub_weakness_query)

    while more_targets_data:
        try:
            resp = r_api.get_target(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in function count_four_or_five_pub_weaknesses calling RandoriApi->get_target: %s\n" % e)
            sys.exit(1)

        more_targets_data = False

    return resp.total



if __name__ == '__main__':
    path = '/Users/bj/.tokens/'

    org_count = 0
    orgs_with_exposed_internal_hn_or_ip = 0
    orgs_with_rdp_exposed = 0
    orgs_with_ssh_exposed = 0
    orgs_with_four_or_five_pub_weakness_exposed = 0

    for filename in os.listdir(path):
        org_count += 1
        print('Processing {}'.format(filename))

        with open((path + filename), 'r+') as f:
            for line in f:
                token = line.rstrip('\n').rstrip(',')

        configuration.access_token = token
        
        internal_host_count = count_internal_hosts()
        
        internal_ip_count = count_internal_ips()
        
    
        if internal_host_count or internal_ip_count:
            orgs_with_exposed_internal_hn_or_ip +=1

        exposed_rdp_count = count_ips_with_ports(3389)

        if exposed_rdp_count:
            orgs_with_rdp_exposed += 1

        exposed_ssh_count = count_ips_with_ports(22)

        if exposed_ssh_count:
            orgs_with_ssh_exposed +=1

        exposed_four_or_five_pub_weakness = count_four_or_five_pub_weaknesses()

        if exposed_four_or_five_pub_weakness:
            orgs_with_four_or_five_pub_weakness_exposed += 1

        sleep(15)

    print(orgs_with_exposed_internal_hn_or_ip, "of", org_count, "Orgs have exposed internal hostnames or ip addresses")

    print(orgs_with_rdp_exposed, "of", org_count, "Orgs have RDP exposed")
    
    print(orgs_with_ssh_exposed, "of", org_count, "Orgs have SSH exposed")

    print(orgs_with_four_or_five_pub_weakness_exposed, "of", org_count, "Orgs have Services with Critical Vulnerabilities exposed")


