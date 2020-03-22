import os
import sys
import warnings

from google.cloud import storage, bigquery

warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

bq_client = bigquery.Client(project='randori-alpha')

storage_client = storage.Client(project='randori-alpha')

bucket_name = 'alpha_missing_affiliations'

local_in_progress_directory = 'in_progress_files'


def notify(text, title):
    os.system("""
            osascript -e 'display notification "{}" with title "{}"
            '""".format(text, title))


def parse_filename(fn):
    # missing_affiliations_31219bf6-8545-4075-9771-950edc0834ed-2019-10-10T14:05:59.042542.txt
    
    parts = fn.split('_')[-1:][0]

    uuid = '-'.join(parts.split('-',5)[:-1])

    date_timestamp = parts.split('-',5)[-1:]


    return (uuid, date_timestamp)



def lookup_org(uuid):
    
    query = "select org_name from stats.orgs where org_id = '%s'" % (uuid)

    query_results = bq_client.query(query, location='US')
    
    for row in query_results: 

        # Row values can be accessed by field name or index
        #assert row[0] == row.org_name == row["org_name"]
        org_name = row['org_name']

        return org_name




def list_blobs():

    blob_list = []

    """Lists all the blobs in the bucket."""

    blobs = storage_client.list_blobs(bucket_name)

    for blob in blobs:
        #print("Blob:", blob)
        if blob.name.startswith('missing_affiliations'):
            blob_list.append(blob.name)

    return blob_list



if __name__ == '__main__':
    org_names = []
    
    file_list = list_blobs()

    for file_name in file_list:

        (uuid, date_timestamp) = parse_filename(file_name)

        org_name = lookup_org(uuid)
        
        if org_name not in org_names:
            org_names.append(org_name)
        
    
    if org_names:
        org_names_string = ','.join(org_names)
        notify(org_names_string, "Missing Affiliations")



