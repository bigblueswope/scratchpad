import json

import common_functions

operation = 'add'

tag = 'CCC'

query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.hostname",
      "operator": "contains",
      "value": "canarycannery"
    },
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    }
  ]
}''')


api_response = common_functions.tag_hostname(operation, tag, query)

print(api_response)



