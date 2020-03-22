import base64
import datetime
import json
import os
import sys

import randori_api
from randori_api.rest import ApiException

from api_tokens import get_api_token

configuration = randori_api.Configuration()

org_name = os.getenv("RANDORI_ENV")

configuration.access_token = get_api_token(org_name);

configuration.host = "https://alpha.randori.io"

r_api = randori_api.RandoriApi(randori_api.ApiClient(configuration))

initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.open_port_count",
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



def iterate_ips_with_ports():
    more_targets_data= True
    offset = 0
    limit = 200
    sort = ['confidence']

    while more_targets_data:
        
        query = prep_query(initial_query)

        try:
            resp = r_api.get_ip(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_ip: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_targets_data = False
        else:
            offset = max_records

        for ip in resp.data:
            print(ip)

                


if __name__ == '__main__':
    iterate_ips_with_ports()
    
