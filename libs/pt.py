import argparse
import os
import sys

from passivetotal.libs.enrichment import EnrichmentRequest

import common_functions


username = "bigblueswope@gmail.com"
api_key = os.getenv('PASSIVETOTAL_API_KEY')

def pt_lookup(domain):

    domain = common_functions.clean_line(domain)

    if not domain:
        # Skip empty lines
        continue
        
    client = EnrichmentRequest.from_config()
        
    results = client.get_subdomains(query=domain)

    try:
        subdomains = results['subdomains']
    except KeyError:
        return None
    
    return subdomains



