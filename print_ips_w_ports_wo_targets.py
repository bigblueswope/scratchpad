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
      "field": "table.open_port_count",
      "operator": "greater",
      "value": 0
    },
    {
      "field": "table.target_count",
      "operator": "equal",
      "value": 0
    }
  ],
  "valid": true
}''')



def prep_query(query_object):

   iq = json.dumps(query_object).encode()

   query = base64.b64encode(iq)

   return query



def iterate_ips():
    more_data= True
    offset = 0
    limit = 200
    sort = ['ip']

    while more_data:
        
        query = prep_query(initial_query)

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
        
        ip_count = 0

        for ip in resp.data:
            ip_count += 1
            print(ip)
            #print(ip.ip, ip.confidence)
        print("Count of IPs with Ports but no Targets: %s" % ip_count)


if __name__ == '__main__':
    iterate_ips()
    
