import argparse
import sys
import warnings

from google.cloud import bigquery

warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")


bq_client = bigquery.Client(project='randori-alpha')

def lookup_org(uuid):

    print("Org UUID:", uuid)

    query = "select org_name from stats.orgs where org_id = '%s'" % (uuid)

    query_results = bq_client.query(query, location='US')

    for row in query_results:
        # Row values can be accessed by field name or index
        #assert row[0] == row.org_name == row["org_name"]
        org_name = row['org_name']

    return org_name


if __name__ == '__main__':
    
    #example_alert_url = 'https://alpha.randori.io/services/c8f95fd9-31be-4fd1-8fea-219b7e2c149b,1e557cd2-337f-4555-aa7f-08c1d43092a0'

    parser = argparse.ArgumentParser(description = 'Decode Randori Service Alert URL')

    required = parser.add_argument_group('required arguments')

    required.add_argument("-i", "--input", required=True, help="URL to Decode")

    args = parser.parse_args()

    uuid = args.input.split(',')[-1:][0]

    org_name = lookup_org(uuid)

    print("Org Name:",org_name)
