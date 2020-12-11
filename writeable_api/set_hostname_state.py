import json

import common_functions


query = json.loads('''{
    "condition": "OR",
    "rules": [
        {
            "field": "table.hostname",
            "operator": "equal",
            "value": "REPLACE_ME"
        }
    ]
}''')

# Example of setting query value
query['rules'][0]['value'] = 'portal.wheezy-wizard.r.canarycannery.com'

assert query['rules'][0]['value'] != 'REPLACE_ME', 'Set the id value in the query.'


# Set impact to High and status to Needs Investigation
api_response = common_functions.set_hostname_state(query, impact_score='High', status='Needs Investigation')

print(api_response)


#Example of an impact that should fail
#api_response = common_functions.set_hostname_state(query, impact_score='Invalid Impact')

#print(api_response)


