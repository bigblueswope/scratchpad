import json
import sys

import common_functions


init_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.name",
      "operator": "equal",
      "value": "Netscaler Gateway"
    },
    {
      "field": "table.hostname",
      "operator": "equal",
      "value": "citrix.webernets.online"
    },
    {
      "field": "table.port",
      "operator": "equal",
      "value": 443
    }
  ],
  "valid": true
}''')

results = common_functions.get_all_detections_for_target(init_query)

netscaler_target_id = results[0].target_id


query = json.loads('''{
    "condition": "OR",
    "rules": [
        {
            "field": "table.id",
            "operator": "equal",
            "value": "REPLACE_ME"
        }
    ]
}''')

# Example of setting query value
query['rules'][0]['value'] = netscaler_target_id

api_response = common_functions.set_target_status_impact(query, impact_score='None', status='None')

print(api_response)



