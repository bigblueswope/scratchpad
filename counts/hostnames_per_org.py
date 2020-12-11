import argparse
import base64
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




def get_host_count():
    
    platform_hosts = []

    offset = 0
    limit = 1
    sort = ['-last_seen']

    query = common_functions.prep_query(initial_query)

    try:

        resp = common_functions.r_api.get_hostname(offset=offset, limit=limit,
                                sort=sort, q=query)

    except common_functions.ApiException as e:

        print("Exception in RandoriApi->get_hostname: %s\n" % e)

        sys.exit(1)

    try:
        return (resp.total, resp.data[0].last_seen)
    except IndexError:
        return (resp.total, '1970-01-01T00:00:00.000000+00:00')




if __name__ == '__main__':
    print("org_name,host_count,last_seen")

    for org_name in common_functions.get_orgs():

        common_functions.configuration.access_token = common_functions.get_api_token(org_name);

        host_count, last_seen = get_host_count()
    
        foo = ','.join([org_name, str(host_count), last_seen])

        print(foo)
    
    
    
