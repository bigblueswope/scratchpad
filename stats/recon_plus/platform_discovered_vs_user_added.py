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



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Iterates all domains for an org and separates into lists')
    optional = parser._action_groups.pop()

    optional.add_argument("-v", "--verbose", default=False, action="store_true",
        help="If the verbose arg/flag is provided, print domains to std out.")

    optional.add_argument("-u", "--user_added", default=False, action="store_true",
        help="If the user arg/flag is provided, print user provided domains to std out.")

    optional.add_argument("-p", "--platform_discovered", default=False, action="store_true",
        help="If the platform discovered arg/flag is provided, print platform discovered domains to std out.")

    parser._action_groups.append(optional)

    args = parser.parse_args()

    headers = ['org_name', 'platform_domains', 'user_added_domains', 'platform_hosts', 'user_added_hosts']
    
    header_str = ','.join(headers)
    
    print(header_str)
        
    #Iterate over every org in the Keychain
    for org in common_functions.get_orgs():

        common_functions.configuration.access_token = common_functions.get_api_token(org);

        platform_domains = common_functions.get_hosts(initial_query)

        discovered_domains = []
        user_domains = []
        
        discovered_hostnames = []
        user_hostnames = []
        
        stats_line = [org]

        for entity in platform_domains:

            entity_type, _, _ = entity_detector.detect_entity(entity.hostname)

            if entity_type == 'domains' and entity.confidence == 100:
                user_domains.append(entity.hostname)

            elif entity_type == 'hostnames' and entity.confidence == 100:
                user_hostnames.append(entity.hostname)

            elif entity_type == 'domains' :
                discovered_domains.append(entity.hostname)

            else:
                discovered_hostnames.append(entity.hostname)
    
        if args.verbose:
            print("Platform Discovered Domains: %s" % discovered_domains)
            print()
            print("User Added Domains: %s" % user_domains)
            print()
            print("Platform Discovered Hostnames: %s" % discovered_hostnames)
            print()
            print("User Added Hostnames %s" % user_hostnames)
    
        if args.user_added:
            print("User Added Domains: %s" % user_domains)
            print()
            print("User Added Hostnames: %s" % user_hostnames)
    
        if args.platform_discovered:
            print("Platform Discovered Domains: %s" % discovered_domains)
            print()
            print("Platform Discovered Hostnames: %s" % discovered_hostnames)
        
        dd_len = str(len(discovered_domains))
        stats_line.append(dd_len)
    
        ud_len = str(len(user_domains))
        stats_line.append(ud_len)

        dh_len = str(len(discovered_hostnames))
        stats_line.append(dh_len)
        
        uh_len = str(len(user_hostnames))
        stats_line.append(uh_len)
        
        stats_str = ','.join(stats_line)

        print(stats_str)
    
