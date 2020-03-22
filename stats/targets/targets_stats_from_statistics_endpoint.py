import argparse
import base64
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



def historical_target_counts(ttype, interval, count):

    if ttype in ('targets', 'top_targets'):
        initial_query['rules'][2]['value'] = ttype
    else:
        print("Target Type must be either targets or top_targets")
        sys.exit(1)

    interval = interval

    limit = count

    sort = ['-time']

    query = common_functions.prep_query(initial_query)

    
    try:
        da_funct = getattr(common_functions.r_api, 'get_statistics')

        resp = da_funct(sort=sort, interval=interval, limit=limit, q=query)

    except common_functions.ApiException as e:

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

    # Two types of targets to count on the Trending Graph in Dashboard
    ttype = 'targets'
    #ttype = 'top_targets'

    # Interval of 144 = 1 Day
    interval = 144

    # Get the stats for 90 days
    count = 90
    
    daily_counts = {}

    if args.Org:

        org = args.Org

        common_functions.configuration.access_token = common_functions.get_api_token(org)
        
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
    
    for org in common_functions.get_orgs():

        sleep(1)

        sys.stderr.write('Processing %s\n' % org)
        
        common_functions.configuration.access_token = common_functions.get_api_token(org)
        
        stats = historical_target_counts(ttype, interval, count)

        for stat in stats.data:
            
            time_str = stat.time.strftime("%Y-%m-%d")
            
            target_count = stat.value
            
            try:
                daily_counts[time_str] += target_count
            
            except KeyError:
                
                daily_counts[time_str] = target_count
        
    for dte, count in daily_counts.items():
        
        print("%s,%i" % (dte, count))


