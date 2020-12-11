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

confidence_suppliment = json.loads('''{
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": ""
    }''')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Print Domains in the Platform')

    optional = parser._action_groups.pop()

    optional.add_argument("-o", "--output", default=False, 
        help="If the output arg/flag is provided, write missing domains to outfile.")

    optional.add_argument("-c", "--confidence", 
        help="Optional minimum confidence domain to return. 25=Low, 60=Medium, 75=High, 100=Prime Entities")

    optional.add_argument("-v", "--verbose", default=False, action="store_true",
        help="Print confidence in output.")

    parser._action_groups.append(optional)

    args = parser.parse_args()

    if args.confidence:

        if args.confidence not in [ '25', '60', '75' , '99', '100']:

            print("If providing the confidence argument please use one of the following integers:\n\t25 = Low\n\t60 = Medium\n\t75 = High")

            sys.exit(1)
        
        confidence_suppliment['value'] = args.confidence

        initial_query['rules'].append(confidence_suppliment)

    sys.stderr.write("\n###################\nDomains:\n")

    platform_domains = common_functions.get_hosts(initial_query)

    actual_domains = []

    non_domains = []

    count_of_non_domains = 0

    for dom in platform_domains:

        ent_type, _, _ = entity_detector.detect_entity(dom.hostname)

        if ent_type == 'domains':

            actual_domains.append(dom.hostname)

            if args.verbose:
                
                print(dom.hostname, dom.confidence)
            
            else:
            
                print(dom.hostname)
        
        else:
            
            count_of_non_domains +=1
            
            non_domains.append(dom.hostname)

    # will write the domains to be added to an outfile
    if args.output:
    
        with open(args.output, 'w+') as outfile:

            for name in actual_domains:

                outfile.write("%s\n" % (name))

    print(f'Count of hostnames marked as domains: {count_of_non_domains}')
    
    print(non_domains)

