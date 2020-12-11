import argparse
import base64
import datetime
import csv
import json
import os
import sys

import common_functions
import entity_detector

from google.cloud import bigquery


mediums_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "field": "table.first_seen",
      "operator": "greater",
      "value": ""
    }
  ],
  "valid": true
}''')


def count_entities(dte):

    results = []

    mediums_query['rules'][1]['value'] = dte

    hostnames = common_functions.get_hosts(mediums_query)

    try:
    
        org_id = hostnames[0].org_id
        
    except IndexError:
        
        if dte == '1970-01-01':

            # If the query is for ALL hostnames and there are no hostnames
            #  there's no sense in running the other queries.
            #  because without hostnames there can be no other entities
            #  so just return an list with an empty org_id and 0 counts

            return (['', 0, 0, 0, 0, 0])
        
        else:

            # There certainly may not be any NEW hostnames
            # If there are no hostnames then we cannot insert the org_id
            # But there certainly may be other NEW entities so do the work
            
            org_id = ''
    
    targets = common_functions.get_targets(mediums_query)

    services = common_functions.get_services(mediums_query)

    ips = common_functions.get_ips(mediums_query)

    networks = common_functions.get_networks(mediums_query)
    
    results.append(org_id)
    
    results.append(len(targets))

    results.append(len(services))

    results.append(len(hostnames))

    results.append(len(ips))

    results.append(len(networks))

    return results




def build_query_string(all_orgs_entity_counts):
    
    #insert into bjs_stats.org_entity_counts values ('asdf-asdf-asdf-asdf', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 '2020-08-02 00:00:00')

    query_string = "INSERT INTO bjs_stats.org_entity_counts VALUES "

    for data in all_orgs_entity_counts:
        org_id = data[0]
        targets_all = data[1]
        services_all = data[2]
        hostnames_all = data[3]
        ips_all = data[4]
        networks_all = data[5]
        targets_new = data[6]
        services_new = data[7]
        hostnames_new = data[8]
        ips_new = data[9]
        networks_new = data[10]
        timestamp = datetime.datetime.now()
        
        if org_id == '':
            
            # if org_id is blank, the org has no hostnames 
            # and therefore cannot have any other entities 
            # so no reason to put them in the stats

            record_string = ''

        else:

            record_string = ( 
                                f"('{org_id}', "
                                f"{targets_new}, {services_new}, "
                                f"{hostnames_new}, {ips_new}, "
                                f"{networks_new}, "
                                f"{targets_all}, {services_all}, "
                                f"{hostnames_all}, {ips_all}, "
                                f"{networks_all}, "
                                f"'{timestamp}'), "
                            )

        query_string = query_string + record_string 

    query_string = query_string.strip(' ,')

    return query_string




if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Iterates over all orgs, filters for medium or higher entities.  \
                                                    Counts total entities and entites < 7 days old. \
                                                    Inserts the counts in a Big Query Db.')
    args = parser.parse_args()

    all_orgs_entity_counts = []

    count = 0

    for org_name in common_functions.get_orgs():
        
        print(org_name)

        count += 1

        common_functions.configuration.access_token = common_functions.get_api_token(org_name);

        entity_counts = []
    
        all_time = '1970-01-01'
    
        all_entities = count_entities(all_time)

        for x in all_entities:
            entity_counts.append(x)
    
        one_week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).date().isoformat()
    
        new_entities = count_entities(one_week_ago)
    
        #no need to re-append org_id to the list
        for x in new_entities[1:]:
            entity_counts.append(x)
        
        all_orgs_entity_counts.append(entity_counts)

    qs = build_query_string(all_orgs_entity_counts)

    print(qs)

    #client = bigquery.Client()
    client = bigquery.Client.from_service_account_json("/Users/bj/.config/gcloud/org_entity_counts_service_account.json")

    query_job = client.query(qs)

    results = query_job.result()

    print(results)
    
    print(f"{count} orgs evaluated")

