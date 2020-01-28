from __future__ import print_function

import base64
import datetime
import json
import logging
import logging.handlers
import os
from pathlib import Path
import pprint
import sys

import randori_api
from randori_api.rest import ApiException

configuration = randori_api.Configuration()

configuration.access_token = os.getenv("RANDORI_API_KEY");

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


def iterate_detection_targets():

    pp = pprint.PrettyPrinter(indent=4)

    more_targets_data= True
    offset = 0
    limit = 200
    sort = ['hostname']

    while more_targets_data:
        
        query = prep_query(initial_query)

        try:
            resp = r_api.get_detection_target(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_target: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_targets_data = False
        else:
            offset = max_records

        for detection_target in resp.data:
            print(detection_target)
            print()
            #pp_detection_target = json.loads(detection_target, indent=2, sort_keys=True)
                


if __name__ == '__main__':
    iterate_detection_targets()
    
