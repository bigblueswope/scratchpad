import argparse
import base64
import json
import os
import sys

import common_functions
import entity_detector

#Initial Query:
#    Confidence Greater Than or Equal To Zero
initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 0
    }
  ],
  "valid": true
}
''')


def get_platform_ips():
    
    platform_ips = {}

    more_data= True
    offset = 0
    limit = 200
    sort = ['confidence']

    while more_data:
        
        query = common_functions.prep_query(initial_query)

        try:
            resp = common_functions.r_api.get_ip(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except common_functions.ApiException as e:
            print("Exception in RandoriApi->get_ip: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_data = False
        else:
            offset = max_records

        for ip in resp.data:

            if not ip.ip in platform_ips.keys():

                platform_ips[ip.ip] = ip.confidence

    return platform_ips

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Compare File With IPs to Existing IPs in Platform')

    optional = parser._action_groups.pop()

    required = parser.add_argument_group('required arguments')

    required.add_argument("-i", "--input", required=True, 
        help="File with possible additional ips")

    optional.add_argument("-o", "--output", default=False, 
        help="If the output arg/flag is provided, write missing ips to outfile.")

    parser._action_groups.append(optional)

    args = parser.parse_args()

    platform_ips = get_platform_ips()

    addl_ips= []
    both_ips = {}
    low_confidence_ips = {}
    non_ips = []
    src_duplicates = 0

    with open(args.input, 'r+') as f:
        for line in f:

            new_ip = common_functions.line_cleaner(line)

            entity_type, _, _ = entity_detector.detect_entity(new_ip)

            if not entity_type == 'ips':
                non_ips.append(new_ip)
                continue
            
            if new_ip in addl_ips:
                src_duplicates += 1
                continue

            if new_ip in platform_ips.keys():
                if platform_ips[new_ip] < 60:
                    low_confidence_ips[new_ip] = platform_ips[new_ip]
                else:
                    try:
                        both_ips[new_ip] = platform_ips[new_ip]
                    except KeyError:
                        # ip is a dupe from the source file
                        src_duplicates += 1
                        continue
            else:
                addl_ips.append(new_ip)
    
    print("\n###################\n")
    print("New IPs To Add To Platform:")

    for ip in addl_ips:
        print(ip)
    
    if args.output:
        with open(args.output, 'w+') as outfile:
            for ip in addl_ips:
                outfile.write(ip)
                outfile.write('\n')
            
    
    sys.stderr.write("\nCount of New IPs: %i\n" % len(addl_ips))

    sys.stderr.write("\nCount of duplicates in source file: %i\n" % src_duplicates)

    sys.stderr.write("\nCount of Med or Higher IPs in source file: %i\n" % len(both_ips))

    sys.stderr.write("\nCount of Low Conf IPs in source file: %i\n" % len(low_confidence_ips))

    sys.stderr.write("\nMedium or Greater Confidence IPs in Platform and Input file: %s\n" % both_ips)

    sys.stderr.write("\nLow or Lesser Confidence IPs in Platform and Input file:%s\n" % low_confidence_ips)
    
    sys.stderr.write("\nNon-IP entities in input file: %s\n" % non_ips)


