import argparse
import sys
import warnings
import json

from google.cloud import bigquery

warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")


bq_client = bigquery.Client(project='randori-alpha')

def lookup_org(uuid):

    print("Org UUID:", uuid)

    query = "select org_name from stats.orgs where org_id = '%s'" % (uuid)

    query_results = bq_client.query(query, location='US')
    
    for row in query_results:
        org_name = row['org_name']

    return org_name


if __name__ == '__main__':

    # example_google_bucket_url = 'https://storage.cloud.google.com/alpha_missing_affiliations/missing_affiliations_cdd75644-15c1-4574-99f4-bd49b9fa394c-2019-12-18T19%3A45%3A19.855472.txt'

    parser = argparse.ArgumentParser(description = 'Decode Missed Affiliation URL')

    required = parser.add_argument_group('required arguments')

    required.add_argument("-i", "--input", required=True, help="URL to Decode")

    args = parser.parse_args()

    uuid = args.input.split('/')[-1:][0]

    uuid = uuid.split('_',2)[2]

    uuid = '-'.join(uuid.split('-',5)[0:5])

    print(uuid)

    org_name = lookup_org(uuid)

    print("Org Name:",org_name)
