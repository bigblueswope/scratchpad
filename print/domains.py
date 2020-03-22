import argparse
import base64
import datetime
import json
import os
import sys

import common_functions
import entity_detector


#Initial Query:
#    Name Type = Domain
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.name_type",
      "operator": "equal",
      "value": 0
    }
  ],
  "valid": true
}''')




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Print Domains in the Platform')

    optional = parser._action_groups.pop()

    optional.add_argument("-o", "--output", default=False, 
        help="If the output arg/flag is provided, write missing domains to outfile.")

    parser._action_groups.append(optional)

    args = parser.parse_args()

    sys.stderr.write("\n###################\nDomains:\n")


    platform_domains = common_functions.get_hostnames(initial_query)
    

    for dom in platform_domains:

        ent_type, _, _ = entity_detector.detect_entity(dom.hostname)

        if ent_type == 'domains':
            print(dom.hostname)
        else:
            platform_domains.remove(dom)

    # will write the domains to be added to an outfile
    if args.output:
    
        with open(args.output, 'w+') as outfile:

            for dom in platform_domains:

                ent_type, _, _ = entity_detector.detect_entity(dom.hostname)

                if ent_type == 'domains':
                    
                    outfile.write("%s\n" % (dom.hostname))

    

    print("************************")
    print(platform_domains)
