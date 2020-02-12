import argparse
import base64
import json
import os
import sys

import randori_api
from randori_api.rest import ApiException

from time import sleep

configuration = randori_api.Configuration()

configuration.access_token = os.getenv("RANDORI_API_KEY");

configuration.host = "https://alpha.randori.io"

r_api = randori_api.RandoriApi(randori_api.ApiClient(configuration))


#Initial Query:
#    Confidence Greater Than or Equal To Medium
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.current",
      "operator": "equal",
      "value": false
    },
    {
      "field": "table.latest",
      "operator": "equal",
      "value": false
    },
    {
      "field": "table.name",
      "operator": "equal",
      "value": "REPLACE_ME"
    }
  ]
}''')



def prep_query(query_object):

   iq = json.dumps(query_object).encode()

   query = base64.b64encode(iq)

   return query



def historical_target_counts(ttype, interval, count):

    if ttype in ('targets', 'top_targets'):
        initial_query['rules'][2]['value'] = ttype
    else:
        print("Target Type must be either targets or top_targets")
        sys.exit(1)

    interval = interval

    limit = count

    sort = ['-time']

    query = prep_query(initial_query)

    
    try:
        da_funct = getattr(r_api, 'get_statistics')
        resp = da_funct(sort=sort, interval=interval, limit=limit, q=query)

    except ApiException as e:
        print("Exception in RandoriApi->%s: %s\n" % ('get_statistics',e))
        sys.exit(1)


    return resp


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'A script to retrieve total counts of entities')

    optional = parser._action_groups.pop()

    optional.add_argument ("-O", "--Org", 
        help="If Org arg is specified, only print target count for the specified Org.")
    
    optional.add_argument ("-v", "--verbose", action='store_true', default=False,
        help="If verbose flag is given, print endpoint name with the count.")

    parser._action_groups.append(optional)

    args = parser.parse_args()


    path = '/Users/bj/.tokens/'

    ttype = 'top_targets'
    interval = 144
    count = 90
    
    daily_counts = {}

    if args.Org:
        filename = args.Org
        
        with open((path + filename), 'r+') as f:
            for line in f:
                token = line.rstrip('\n').rstrip(',')
        configuration.access_token = token
        
        stats = historical_target_counts(ttype, interval, count)

        for stat in stats.data:
            time_str = stat.time.strftime("%Y-%m-%d")
            target_count = stat.value
            
            try:
                daily_counts[time_str] += target_count
            except KeyError:
                daily_counts[time_str] = target_count
        
        print(daily_counts)
        sys.exit(0)


    total_targets = 0
    
    for filename in os.listdir(path):
        sleep(1)
        sys.stderr.write('Processing %s\n' %filename)
        
        with open((path + filename), 'r+') as f:
            for line in f:
                token = line.rstrip('\n').rstrip(',')
        
        configuration.access_token = token
        
        stats = historical_target_counts(ttype, interval, count)

        for stat in stats.data:
            time_str = stat.time.strftime("%Y-%m-%d")
            target_count = stat.value
            
            try:
                daily_counts[time_str] += target_count
            except KeyError:
                daily_counts[time_str] = target_count
        
    print(daily_counts)
