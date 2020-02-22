import base64
import datetime
import json
import logging
import logging.handlers
import os
from pathlib import Path
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


#Initial Query:
#    Confidence Greater Than or Equal To Medium
#    and
#    Port # and Port is open

initial_query = json.loads('''{
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
      "value": 1433
    },
    {
      "field": "table.state",
      "operator": "equal",
      "value": "open"
    }
  ],
  "valid": true
  }''')


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

##########
# Sample JSON returned by get_ports_for_ip
##########
'''
{'confidence': 75,
 'deleted': False,
 'id': 'fa65b758-1636-41d9-823e-b78c552aff62',
 'ip_id': '8c3e21b0-a6e7-4f46-bff9-2ed8575e7525',
 'last_seen': datetime.datetime(2019, 10, 7, 12, 25, 56, 107949, tzinfo=tzutc()),
 'max_confidence': 75,
 'org_id': '71803330-934a-4c4d-bd82-af1ba5e73ae8',
 'port': 443,
 'protocol': 6,
 'seen_open': True,
 'state': 'open'}
 '''


def iterate_ips_with_ports():
    more_targets_data= True
    offset = 0
    limit = 200
    sort = ['port']

    while more_targets_data:
        
        query = prep_query(initial_query)

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
            print(ip)
            #print(ip.port)
                


if __name__ == '__main__':
    iterate_ips_with_ports()
    
