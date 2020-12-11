import json

import common_functions

initial_query = json.loads('''{
  "condition": "AND",
  "rules": [
    {
      "field": "table.tags",
      "operator": "has_key",
      "value": "YOUR TAG HERE"
    }
  ]
}''')

#Example method to assign rules value
initial_query['rules'][0]['value'] = 'Cert Expired'

assert initial_query['rules'][0]['value'] != 'YOUR TAG HERE', 'Change the value field to be the tag for which you wish to query'

try:

    for host in common_functions.get_hosts(initial_query):

        print(host)
        print('#######################')

except Exception as e:

    print(e)
 


