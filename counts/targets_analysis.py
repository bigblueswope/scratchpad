import argparse
import base64
import csv
import json
import os
import sys

import common_functions
import entity_detector


conf_100_query = json.loads('''{
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


conf_60_query = json.loads('''{
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


detections_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.hostname",
      "operator": "equal",
      "value": ""
    }
  ],
  "valid": true
}''')



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Iterates all hosts for an org and separates into lists')

    org_name = os.getenv("RANDORI_ENV")

    org_dict = {}

    pe_doms = {}
    
    orphan_hosts = []

    target_ids = []

    # retrieves entities with 100 confidence
    pes = common_functions.get_hosts(conf_100_query)


    for ent in pes:
        
        ent_type, ent_name, dom = entity_detector.detect_entity(ent.hostname)

        if ent_type == 'domains':

            pe_doms[dom] = {}
            pe_doms[dom]['dom_name'] = dom
            #pe_doms[dom]['confidence'] = ent.confidence
            pe_doms[dom]['first_seen'] = ent.first_seen.split('+')[0].replace('T', ' ')
            pe_doms[dom]['user_hosts'] = 0
            pe_doms[dom]['plat_hosts'] = 0
            pe_doms[dom]['total_detections'] = 0
            pe_doms[dom]['unique_detections'] = 0
            pe_doms[dom]['user_critical_targets'] = 0
            pe_doms[dom]['plat_critical_targets'] = 0
            pe_doms[dom]['user_high_targets'] = 0
            pe_doms[dom]['plat_high_targets'] = 0
            pe_doms[dom]['user_medium_targets'] = 0
            pe_doms[dom]['plat_medium_targets'] = 0
            pe_doms[dom]['user_low_targets'] = 0
            pe_doms[dom]['plat_low_targets'] = 0
            pe_doms[dom]['unscored_targets'] = 0
        
    
    hostname_entities = common_functions.get_hosts(conf_60_query)

    for ent in hostname_entities:
        
        detections_query['rules'][0]['value'] = ent.hostname

        detections = common_functions.get_single_detection_for_target(detections_query)
        
        ent_type, ent_name, dom = entity_detector.detect_entity(ent.hostname)
        
        if ent.confidence == 100:
            
            try:
                
                pe_doms[dom]['user_hosts'] += 1

                for detection in detections:
                    
                    pe_doms[dom]['total_detections'] += 1
                    
                    if detection.target_id not in target_ids:
                        
                        pe_doms[dom]['unique_detections'] += 1
                        
                        target_ids.append(detection.target_id)
                    
                    if 0 < detection.target_temptation < 15:
                    
                        pe_doms[dom]['user_low_targets'] += 1
                    
                    elif 15 <= detection.target_temptation < 30:
                    
                        pe_doms[dom]['user_medium_targets'] += 1
                    
                    elif 30 <= detection.target_temptation < 40:
                        
                        pe_doms[dom]['user_high_targets'] += 1
                        
                    elif 40 <= detection.target_temptation <= 100:
                        
                        pe_doms[dom]['user_critical_targets'] += 1
                    
                    else:
                    
                        pe_doms[dom]['unscored_targets'] += 1
            
                    
            except KeyError:
                
                orphan_hosts.append(ent.hostname)
        else:

            try:
                
                pe_doms[dom]['plat_hosts'] += 1
                
                for detection in detections:
                    
                    pe_doms[dom]['total_detections'] += 1
                    
                    if detection.target_id not in target_ids:
                        
                        pe_doms[dom]['unique_detections'] += 1
                        
                        target_ids.append(detection.target_id)
                    
                    if 0 < detection.target_temptation < 15:
                    
                        pe_doms[dom]['plat_low_targets'] += 1
                    
                    elif 15 <= detection.target_temptation < 30:
                    
                        pe_doms[dom]['plat_medium_targets'] += 1
                    
                    elif 30 <= detection.target_temptation < 40:
                        
                        pe_doms[dom]['plat_high_targets'] += 1
                        
                    elif 40 <= detection.target_temptation <= 100:
                        
                        pe_doms[dom]['plat_critical_targets'] += 1
                    
                    else:
                    
                        pe_doms[dom]['unscored_targets'] += 1

            except KeyError:

                orphan_hosts.append(ent.hostname)

    

    print("Prime Entity Domains and Their Prime Children")

    print(json.dumps(pe_doms, indent=4, sort_keys=True))

    print('\n############\nOrphan Hosts')

    print(orphan_hosts)

    outfile = org_name + '.csv'
    
    f = csv.writer(open(outfile, "w"))
    
    
    headers = []

    for x in list(pe_doms)[0:1]:

        for key in pe_doms[x].keys():
            
            headers.append(key)
    

    f.writerow(headers)

    for pe_key in pe_doms.keys():
        
        line_content = []
        
        for fv in headers:
            
            line_content.append(pe_doms[pe_key][fv])
        
        f.writerow(line_content)
