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
      "value": 100
    }
  ],
  "valid": true
}''')




if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Iterates all hosts for an org and separates into lists')
    

    prime_entity_domains = {}
    
    orphan_hosts = []

    # retrieves entities with 100 confidence
    pes = common_functions.get_hosts(initial_query)

    for ent in pes:

        ent_type, ent_name, _ = entity_detector.detect_entity(ent.hostname)

        if ent_type == 'domains':

            prime_entity_domains[ent_name] = []
    

    for ent in pes:
        
        ent_type, ent_name, dom = entity_detector.detect_entity(ent.hostname)
        
        if ent_type == 'hostnames':

            try:
                prime_entity_domains[dom].append(ent_name)
            except KeyError:
                orphan_hosts.append(ent.hostname)


    print("Prime Entity Domains and Their Prime Children")

    print(json.dumps(prime_entity_domains, indent=4, sort_keys=True))

    print('\n############\nOrphan Hosts')

    print(orphan_hosts)
