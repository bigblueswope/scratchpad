import argparse
import base64
import datetime
import csv
import json
import os
import sys

import common_functions
import entity_detector
import api_tokens

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

    mediums_query['rules'][1]['value'] = dte

    hostnames = common_functions.get_hosts(mediums_query)
    
    try:
        org_id = hostnames[0].org_id
    except IndexError:
        # NOTE: Most times the API Framework throws an exception that terminates
        #  execution before we get to this point so this code never really fires.


        # DELETE TOKEN BECAUSE ORG HAS NO HOSTS
        #  Calling function with no arg so the function prompts for Org Name
        #  this is to allow one to check the UI to see if the org is indeeed empty
        #  and thus should no longer have a token in the KeyChain
        api_tokens.delete_api_token()


if __name__ == '__main__':

    for org_name in common_functions.get_orgs():

        print(org_name)

        try:
            common_functions.configuration.access_token = common_functions.get_api_token(org_name)
        except AssertionError:
            print(f'{org_name} does not have an API Token in the Keyring.\nWhen prompted, copy/paste the org name to remove them from the list of orgs in the keyring')
            api_tokens.delete_api_token()
            continue

    
        all_time = '1970-01-01'
    
        all_entities = count_entities(all_time)
    
