import json

import common_functions


query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.id",
      "operator": "equal",
      "value": "REPLACE_ME"
    }
  ],
  "valid": true
}''')

# Example of setting query value
query['rules'][0]['value'] = 'fcd98059-2375-431c-9dfc-871cb47beed6'

assert query['rules'][0]['value'] != 'REPLACE_ME', 'Set the id value in the query.'


# Set Impact to High, Status to Needs Investigation and remove Attack Authorization
api_response = common_functions.set_target_state(query, impact_score='High', status='Needs Investigation', authorization_state = 'None')

print(api_response)


#Example of an impact that should fail
#api_response = common_functions.apply_status_impact_to_hostname(query, impact_score='Invalid Impact')

#print(api_response)


