import argparse
import base64
import datetime
import json
import os
import sys

import common_functions
import entity_detector

# Query looking for substring match of the Service Name
# Note: Search is case sensitive
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.name",
      "operator": "contains",
      "value": ""
    }
  ],
  "valid": true
}''')



def find_targets(initial_query):

    matching_targets = []

    more_targets_data= True
    offset = 0
    limit = 1000
    sort = ['confidence']
    
    query = common_functions.prep_query(initial_query)

    while more_targets_data:
        
        try:
            resp = common_functions.r_api.get_target(offset=offset, limit=limit,
                                    sort=sort, q=query)

        except common_functions.ApiException as e:
            
            print("Exception in RandoriApi->get_target: %s\n" % e)

            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:

            more_targets_data = False

        else:
        
            offset = max_records

        for target in resp.data:
            t_details = {}
            t_details['org'] = org
            t_details['org_id'] = target.org_id
            t_details['ip'] = target.ip_str
            t_details['ip_id'] = target.ip_id

            matching_targets.append(t_details)
    
    return matching_targets

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Search through all orgs looking for targets that match ')

    optional = parser._action_groups.pop()

    required = parser.add_argument_group('required arguments')

    required.add_argument("-n", "--name", required=True, help="Name of Service (may be substring of Service Name)")

    optional.add_argument("-o", "--output", default=False,
        help="If the output arg/flag is provided, write targets to a file.")

    parser._action_groups.append(optional)

    args = parser.parse_args()


    cross_org_targets = []
    

    for org in common_functions.get_orgs():

        print("Processing Org: %s" % org)

        common_functions.configuration.access_token = common_functions.get_api_token(org);

        initial_query['rules'][0]['value'] = args.name

        for target in find_targets(initial_query):

            cross_org_targets.append(target)
    
    print(json.dumps(cross_org_targets, indent=4, sort_keys=True))

    if args.output:

        with open(args.output, 'w+') as f:

            json.dump(cross_org_targets, f, indent=4, sort_keys=True)

            f.write('\n')


