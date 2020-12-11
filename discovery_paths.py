import argparse
import base64
import json
import os
import sys

import common_functions

# Discovery Path Sample Request
#https://alpha.randori.io/recon/api/v1/paths?terminal=8a6a5d42-3ac8-4d70-86ce-58432bd5321f

hostnames_query = json.loads('''{
    "condition": "AND",
    "rules": [
        {
            "field": "table.confidence",
            "operator": "greater_or_equal",
            "value": 60
        }
    ]
}''')

for entity in common_functions.get_hosts(hostnames_query):
    print(entity.id)
    
    paths = common_functions.get_paths(id)

    print(paths)
