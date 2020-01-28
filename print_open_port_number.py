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

configuration = randori_api.Configuration()

configuration.access_token = os.getenv("RANDORI_API_KEY");

configuration.host = "https://alpha.randori.io"

r_api = randori_api.RandoriApi(randori_api.ApiClient(configuration))

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

syslog_server = ''

if syslog_server:
    syslog_handler = logging.handlers.SysLogHandler(address=(syslog_server, 
                                                             514))
    logger.addHandler(syslog_handler)

output_log = ''

if output_log:
    Path(output_log).touch(exist_ok=True)
    file_handler = logging.FileHandler(output_log)
    logger.addHandler(file_handler)

log_to_console = True

if not (output_log or syslog_server) or log_to_console:
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)


#Initial Query:
#    Confidence Greater Than or Equal To Medium
#    and
#    Has Open Ports
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "field": "table.seen_open",
      "operator": "equal",
      "value": true
    }
  ],
  "valid": true
}
''')



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
            print(ip.port)

                


if __name__ == '__main__':
    iterate_ips_with_ports()
    
