from __future__ import print_function 
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

import shodan

configuration = randori_api.Configuration()

configuration.access_token = os.getenv("RANDORI_API_KEY")

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

configuration.host = "https://alpha.randori.io"

r_api = randori_api.RandoriApi(randori_api.ApiClient(configuration))

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

alerts_log = ''

if alerts_log:
    Path(alerts_log).touch(exist_ok=True)
    file_handler = logging.FileHandler(alerts_log)
    logger.addHandler(file_handler)

log_to_console = True

if not alerts_log or log_to_console:
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)


#Initial Query:
#    Confidence Greater Than or Equal To Medium
#    and
#    Target Temptation Greater Than or Equal To High
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "condition": "AND",
      "rules": [
        {
          "field": "table.hostname",
          "operator": "not_contains",
          "value": "randori.com"
        }
      ]
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
# Sample JSON returned by get_hostname
##########
'''
{'confidence': 75,
 'deleted': False,
 'first_seen': datetime.datetime(2019, 9, 13, 20, 18, 45, 334601, tzinfo=tzutc()),
 'hostname': 'www.webernets.online',
 'id': 'bc6a641f-eef5-444f-9311-1d43da55638c',
 'ip_count': 15,
 'last_seen': datetime.datetime(2019, 10, 7, 12, 25, 56, 107949, tzinfo=tzutc()),
 'max_confidence': 75,
 'name_type': 1,
 'org_id': '71803330-934a-4c4d-bd82-af1ba5e73ae8',
 'tags': {},
 'target_temptation': 22}
 '''

def iterate_ips():
    more_targets_data= True
    offset = 0
    limit = 200
    sort = ['hostname']

    while more_targets_data:
        
        query = prep_query(initial_query)

        try:
            resp = r_api.get_ip(offset=offset, limit=limit,
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
            #print(ip)
            ip_addr = ip.ip_str
            print(ip_addr)
            
            api = shodan.Shodan(SHODAN_API_KEY)

            try:
                host = api.host(ip_addr)
            
                print(host['city'], host['region_code'], host['country_code'])
            except:
                pass


if __name__ == '__main__':
    iterate_ips()
    
