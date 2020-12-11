import json

import common_functions

operation = 'add'

tag = 'CCC'

query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.id",
      "operator": "equal",
      "value": "REPLACE_ME"
    }
  ]
}''')

#Set actual value
query['rules'][0]['value'] = 'f49cf10a-851e-4328-a840-8e58222befcb'


api_response = common_functions.tag_ip(operation, tag, query)

print(api_response)



