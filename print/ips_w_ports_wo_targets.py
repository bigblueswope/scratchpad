import base64
import datetime
import json
import os
import sys

import common_functions
import entity_detector

initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    },
    {
      "field": "table.open_port_count",
      "operator": "greater",
      "value": 0
    },
    {
      "field": "table.target_count",
      "operator": "equal",
      "value": 0
    }
  ],
  "valid": true
}''')


ports_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.ip_id",
      "operator": "equal",
      "value": "abcd"
    },
    {
      "field": "table.state",
      "operator": "equal",
      "value": "open"
    }
  ],
  "valid": true
}''')


hostnames_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.ip_id",
      "operator": "equal",
      "value": ""
    }
  ],
  "valid": true
}''')





if __name__ == '__main__':
    for ip in common_functions.get_ips(initial_query):

        hostnames_list = []
        http_url = 'http://'
        https_url = 'https://'

        ip_80 = False
        ip_443 = False
        
        print("############")
        print(ip.id)
        print(ip.ip_str)

        hostnames_query['rules'][0]['value'] = ip.id

        hostnames = common_functions.get_hostnames_for_ip(hostnames_query)

        for hostname in hostnames:

            hostnames_list.append(hostname.hostname)
        
        ports_query['rules'][0]['value'] = ip.id
        
        ports = common_functions.get_ports(ports_query)
        
        for port in ports:
            
            if port.port == 80:
                
                for hostname in hostnames_list:
                    
                    url = http_url + hostname

                    ip_url = http_url + ip.ip_str

                    if not ip_80:
                        print(ip_url)
                        ip_80 = True
                    
                    print(url)
            
            elif port.port == 443:

                for hostname in hostnames_list:

                    url = https_url + hostname

                    ip_url = https_url + ip.ip_str
                    
                    if not ip_443:
                        print(ip_url)
                        ip_443 = True

                    print(url)
                    


    

''' Sample output:

{'affiliation_state': 'None',
 'confidence': 75,
 'country': 'CA',
 'deleted': False,
 'first_seen': '2019-04-17T22:51:17.174452+00:00',
 'hostname': None,
 'hostname_count': 1,
 'id': '16d755ca-f5bd-4669-9a27-e2c882e3b089',
 'impact_score': 'None',
 'ip': '209.202.107.244',
 'ip_str': '209.202.107.244',
 'last_seen': '2020-08-19T18:20:39.324413+00:00',
 'latitude': 43.7806,
 'longitude': -79.3503,
 'max_confidence': None,
 'open_port_count': 4,
 'org_id': '6b9d7087-a497-4a71-9329-dd32b0f93eec',
 'perspective': '00000000-0000-0000-0000-000000000000',
 'perspective_name': 'PUBLIC',
 'radius': None,
 'refreshed': None,
 'service_count': 0,
 'status': 'None',
 'tags': {'INTERESTING+Login': {'content': 'INTERESTING+Login',
                                'display': True,
                                'entity_id': '16d755ca-f5bd-4669-9a27-e2c882e3b089',
                                'org_id': '6b9d7087-a497-4a71-9329-dd32b0f93eec',
                                'time_added': '2019-06-25T12:46:36.647198+00:00'}},
 'target_count': 0,
 'target_temptation': None}

 '''
