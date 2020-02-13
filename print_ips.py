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
#    Target Temptation Greater Than or Equal To Zero
initial_query = json.loads('''{
  "condition": "OR",
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
          "field": "table.target_temptation",
          "operator": "greater_or_equal",
          "value": 0
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

        for ip in resp.data:
            print(ip)
            #print(ip.ip, ip.confidence)
                


if __name__ == '__main__':
    iterate_ips()
    
