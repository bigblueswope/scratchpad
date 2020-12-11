import json
import netaddr
import os

import common_functions
import ipinfo



#IP Info Token
ipinfo_access_token = os.getenv("IPINFO_TOKEN")

assert ipinfo_access_token is not None, 'IPInfo API Token is not set.'

handler = ipinfo.getHandler(ipinfo_access_token)



def tag_ip(tag, ip_id):

    operation = 'add'

    tag = tag

    query = json.loads('''{
        "condition": "OR",
        "rules": [
            {
                "field": "table.id",
                "operator": "equal",
                "value": "REPLACE_ME_WITH_HOST_ID"
            }
        ]
    }''')
    
    query['rules'][0]['value'] = ip_id
    
    api_response = common_functions.tag_ip(operation, tag, query)
        
    print(api_response)



def analyze_ips(entities):
    
    for ip_id, ip_str in entities.items():

        try:
            print(ip_str)
            
            ip = netaddr.IPAddress(ip_str)

            if any( [ ip.is_private(), ip.is_reserved(), ip.is_loopback() ] ):
                
                # tag as internal IP
                tag_ip('Internal', ip_id)
    
            else:
    
                #lookup ip using ipinfo.io
                details = handler.getDetails(ip_str)
                
                # set tag as ASN Name 
                tag = (details.asn['name'])
                
                # then tag the IP with ASN Name
                tag_ip(tag, ip_id)
    
        except ValueError as e:
            
            pass
    
    
    


if __name__ == '__main__':

    initial_query = json.loads('''{
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

    #for org_name in common_functions.get_orgs():
    for org_name in ['webernets']:
        
        print(org_name)

        common_functions.configuration.access_token = common_functions.get_api_token(org_name);
        
        entities = {}
        
        org_ips = common_functions.get_ips(initial_query)

        for entity in org_ips:
            entities[entity.id] = entity.ip
        
        analyze_ips(entities)


