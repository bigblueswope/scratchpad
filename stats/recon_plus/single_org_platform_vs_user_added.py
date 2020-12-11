import argparse
import base64
import datetime
import json
import os
import sys

from pytz import timezone

import api_tokens
from common_functions import get_hosts
#import common_functions
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



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Iterates all domains for an org and separates into lists')
    optional = parser._action_groups.pop()

    optional.add_argument("-o", "--org", help="Org name to compare.")

    optional.add_argument("-v", "--verbose", default=False, action="store_true",
        help="If the verbose arg/flag is provided, print domains to std out.")

    optional.add_argument("-u", "--user_added", default=False, action="store_true",
        help="If the user arg/flag is provided, print user provided domains to std out.")

    optional.add_argument("-p", "--platform_discovered", default=False, action="store_true",
        help="If the platform discovered arg/flag is provided, print platform discovered domains to std out.")

    parser._action_groups.append(optional)

    args = parser.parse_args()

    '''if not args.org:
        org_name = input("Org Name: ")
    else:
        org_name = args.org
    '''
    #common_functions.configuration.access_token = common_functions.get_api_token(org_name);
    #common_functions.configuration.access_token = api_tokens.get_api_token(org);

    platform_domains = get_hosts(initial_query)
    #platform_domains = common_functions.get_hosts(initial_query)
    
    first_domain_list = ['']

    oldest_first_seen = datetime.datetime.now() 
    #oldest_first_seen = datetime.datetime.now(timezone('UTC')) 

    discovered_domains = []
    user_domains = []
    
    discovered_hostnames = []
    user_hostnames = []
    

    for entity in platform_domains:

        entity_type, _, _ = entity_detector.detect_entity(entity.hostname)

        if entity_type == 'domains' and entity.confidence == 100:

            user_domains.append(entity.hostname)
            
            fsd = datetimeObj = datetime.datetime.strptime(entity.first_seen, '%Y-%m-%dT%H:%M:%S.%f+00:00')

            if fsd < oldest_first_seen:
                first_domain_list[0] = entity.hostname
                oldest_first_seen = fsd

        elif entity_type == 'hostnames' and entity.confidence == 100:
            user_hostnames.append(entity.hostname)

        elif entity_type == 'domains' :
            discovered_domains.append(entity.hostname)

        else:
            discovered_hostnames.append(entity.hostname)

    while first_domain_list[0] in user_domains: user_domains.remove(first_domain_list[0])


    if args.verbose:
        print()
        print("Prime Entity Domain\n%s" % first_domain_list)
        print()
        print("Platform Discovered Domains:\n%s" % discovered_domains)
        print()
        print("User Added Domains:\n%s" % user_domains)
        print()
        print("Platform Discovered Hostnames:\n%s" % discovered_hostnames)
        print()
        print("User Added Hostnames:\n%s" % user_hostnames)

