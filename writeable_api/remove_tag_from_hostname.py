import json

import common_functions

operation = 'remove'

tag = 'Webernets'

query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.confidence",
      "operator": "greater_or_equal",
      "value": 60
    }
  ]
}''')

api_response = common_functions.tag_hostname(operation, tag, query)

# Note: If the operation succeeds the api_respones is
#  a count of entities that matched the query
#  not a count of how many entities had the tag removed.
#  If an entity matches the query, but it did not have the tag
#  nothing happens but the count is not a reflection of how
#  many tags were actually removed.

print(api_response)

