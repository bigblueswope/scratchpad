import base64
import json
import os
import sys

import randori_api
from randori_api.rest import ApiException

from api_tokens import get_api_token, get_orgs


configuration = randori_api.Configuration()

org_name = os.getenv("RANDORI_ENV")

configuration.access_token = get_api_token(org_name)

configuration.host = "https://alpha.randori.io"

r_api = randori_api.DefaultApi(randori_api.ApiClient(configuration))


valid_affiliation_states = [ 'None', 'Unaffiliated' ]

valid_authorization_states = [ 'None', 'Authorized' ]

valid_impacts = [ 'None', 'Low', 'Medium', 'High' ]

valid_statuses = [ 'None', 'Accepted', 'Mitgated', 'Needs Investigation', 'Needs Resolution', 'Needs Review' ]

valid_patch_inputs = { 'affiliation_state': valid_affiliation_states, 
    'authorization_state': valid_authorization_states, 
    'impact_score': valid_impacts, 
    'status': valid_statuses }

valid_tag_operations = [ 'add', 'remove' ]

invalid_tag_chars = [ ',', '/' ]



def tag_cleaner(tag):
    
    for char in invalid_tag_chars:
        
        tag = tag.replace(char, '')
    
    return tag


def line_cleaner(line):

    if ',' in line:
        #assumes domain/host is first entry in the CSV line
        line = line.split(',')[0]

    if '#' in line:
        # Treating # as an in-line comment so split on # for the first field
        line = line.split('#')[0]

    line = line.strip('*\n.,"\t ').lower()

    if line == 'domainname':
        # Skip empty line or line with value of "domainname"
        return None
    
    return line



def prep_query(query_object):

   iq = json.dumps(query_object).encode()

   query = base64.b64encode(iq)

   return query


def conf_to_stirng(conf):
    if conf == 100:
        return 'Max'
    elif conf >=  90:
        return 'Extreme'
    elif conf >= 75:
        return 'High'
    elif conf >= 60:
        return 'Medium'
    elif conf >= 25:
        return 'Low'
    else:
        return 'Min'
        

def tt_to_string(tt):
    if tt >= 40:
        return 'Critical'
    elif tt >= 30:
        return 'High'
    elif tt >= 15:
        return 'Medium'
    else:
        return 'Low'


def priority_to_string(priority):
    if priority >= 29.98:
        return 'High'
    elif priority > 20:
        return 'Medium'
    else:
        return 'Low'



def get_all_detections_for_target(query):
    detections = []

    more_targets_data = True
    offset = 0
    limit = 1000
    sort = ['-last_seen']

    query = prep_query(query)

    while more_targets_data:

        try:
            resp = r_api.get_all_detections_for_target(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi-get_all_detections_for_target: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit

        if resp.total <= max_records:
            more_targets_data = False
        else:
            offset = max_records

        for detection in resp.data:
            detections.append(detection)

    return detections



def get_hosts(query):
    hosts = []

    more_targets_data = True
    offset = 0
    limit = 1000
    sort = ['hostname']

    query = prep_query(query)

    while more_targets_data:

        try:
            resp = r_api.get_hostname(offset=offset, limit=limit,
                                    sort=sort, q=query)

        except ApiException as e:

            print("Exception in RandoriApi->get_hostname: %s\n" % e)

            sys.exit(1)

        max_records = offset + limit

        if resp.total <= max_records:

            more_targets_data = False

        else:

            offset = max_records

        for host in resp.data:

            hosts.append(host)

    return hosts




def get_hostnames_for_ip(query):
    hosts = []

    more_targets_data = True
    offset = 0
    limit = 1000
    sort = ['hostname']

    query = prep_query(query)

    while more_targets_data:

        try:
            resp = r_api.get_hostnames_for_ip(offset=offset, limit=limit,
                                    sort=sort, q=query)

        except ApiException as e:

            print("Exception in RandoriApi->get_hostname: %s\n" % e)

            sys.exit(1)

        max_records = offset + limit

        if resp.total <= max_records:

            more_targets_data = False

        else:

            offset = max_records

        for host in resp.data:

            hosts.append(host)

    return hosts




def get_ips(query):
    ips = []

    more_data= True
    offset = 0
    limit = 1000
    sort = ['ip']

    query = prep_query(query)

    while more_data:

        try:
            resp = r_api.get_ip(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_ip: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit

        if resp.total <= max_records:
            more_data = False
        else:
            offset = max_records

        for ip in resp.data:
            ips.append(ip)

    return ips



def get_networks(query):
    networks = []

    more_data= True
    offset = 0
    limit = 1000
    sort = ['confidence']

    query = prep_query(query)

    while more_data:

        try:
            resp = r_api.get_network(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_network: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit

        if resp.total <= max_records:
            more_data = False
        else:
            offset = max_records

        for network in resp.data:
            networks.append(network)

    return networks


def get_paths(id):
    paths = []

    try:
    
        resp = r_api.paths(terminal=id)
    
    except ApiException as e:
        print(f'Exception in RandoriApi->paths:\n{e}')
        sys.exit(1)

    for path in resp.data:
        paths.append(path)

    return paths




def get_ports(query):
    ports = []

    more_targets_data = True
    offset = 0
    limit = 1000
    sort = ['port']

    query = prep_query(query)

    while more_targets_data:
        
        try:
            resp = r_api.get_ports_for_ip(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_ports_for_ip: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_targets_data = False
        else:
            offset = max_records

        for port in resp.data:
            ports.append(port)

    return ports



def get_single_detection_for_target(query):
    single_detections = []

    more_targets_data = True
    offset = 0
    limit = 1000
    sort = ['hostname']

    query = prep_query(query)

    while more_targets_data:

        try:
            resp = r_api.get_single_detection_for_target(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_single_detection_for_target: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit

        if resp.total <= max_records:
            more_targets_data = False
        else:
            offset = max_records

        for sd in resp.data:
            single_detections.append(sd)

    return single_detections




def get_services(query):
    services = []

    more_services_data = True
    offset = 0
    limit = 1000
    sort = ['-target_temptation']

    query = prep_query(query)

    while more_services_data:
        
        try:
            resp = r_api.get_service(offset=offset, limit=limit,
                                    sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_service: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_services_data = False
        else:
            offset = max_records

        for service in resp.data:
            services.append(service)

    return services



def get_targets(query):
    targets = []

    more_targets_data = True
    offset = 0
    limit = 1000
    sort = ['-target_temptation']

    query = prep_query(query)

    while more_targets_data:
        
        try:
            resp = r_api.get_target(offset=offset, limit=limit, sort=sort, q=query)
        except ApiException as e:
            print("Exception in RandoriApi->get_target: %s\n" % e)
            sys.exit(1)

        max_records = offset + limit
    
        if resp.total <= max_records:
            more_targets_data = False
        else:
            offset = max_records

        for target in resp.data:
            targets.append(target)

    return targets




def print_raw_all_detections_for_target(query):
    targets = []

    offset = 0
    limit = 1
    sort = ['-target_temptation']

    query = prep_query(query)

    try:
        resp = r_api.get_all_detections_for_target(offset=offset, limit=limit, sort=sort, q=query)
    except ApiException as e:
        print("Exception in RandoriApi->get_all_detections_for_target: %s\n" % e)
        sys.exit(1)

    print(resp)


def print_raw_hostname(query):
    targets = []

    offset = 0
    limit = 1
    sort = ['-target_temptation']

    query = prep_query(query)

    try:
        resp = r_api.get_hostname(offset=offset, limit=limit, sort=sort, q=query)
    except ApiException as e:
        print("Exception in RandoriApi->get_hostname: %s\n" % e)
        sys.exit(1)

    print(resp)


def print_raw_hostname_for_ip(query):
    targets = []

    offset = 0
    limit = 1
    sort = ['-hostname']

    query = prep_query(query)

    try:
        resp = r_api.get_hostnames_for_ip(offset=offset, limit=limit, sort=sort, q=query)
    except ApiException as e:
        print("Exception in RandoriApi->get_hostnames_for_ip: %s\n" % e)
        sys.exit(1)

    print(resp)


def print_raw_ip(query):
    targets = []

    offset = 0
    limit = 1
    sort = ['-target_temptation']

    query = prep_query(query)

    try:
        resp = r_api.get_ip(offset=offset, limit=limit, sort=sort, q=query)
    except ApiException as e:
        print("Exception in RandoriApi->get_ip: %s\n" % e)
        sys.exit(1)

    print(resp)


def print_raw_network(query):
    targets = []

    offset = 0
    limit = 1
    sort = ['-target_temptation']

    query = prep_query(query)

    try:
        resp = r_api.get_network(offset=offset, limit=limit, sort=sort, q=query)
    except ApiException as e:
        print("Exception in RandoriApi->get_network: %s\n" % e)
        sys.exit(1)

    print(resp)


def print_raw_port(query):
    targets = []

    offset = 0
    limit = 1
    sort = ['-confidence']

    query = prep_query(query)

    try:
        resp = r_api.get_ports_for_ip(offset=offset, limit=limit, sort=sort, q=query)
    except ApiException as e:
        print("Exception in RandoriApi->get_ports_for_ip: %s\n" % e)
        sys.exit(1)

    print(resp)


def print_raw_service(query):
    targets = []

    offset = 0
    limit = 1
    sort = ['-target_temptation']

    query = prep_query(query)

    try:
        resp = r_api.get_service(offset=offset, limit=limit, sort=sort, q=query)
    except ApiException as e:
        print("Exception in RandoriApi->get_service: %s\n" % e)
        sys.exit(1)

    print(resp)


def print_raw_target(query):
    targets = []

    offset = 0
    limit = 1
    sort = ['-target_temptation']

    query = prep_query(query)

    try:
        resp = r_api.get_target(offset=offset, limit=limit, sort=sort, q=query)
    except ApiException as e:
        print("Exception in RandoriApi->get_target: %s\n" % e)
        sys.exit(1)

    print(resp)



def build_tag_operation(operation, tag):

    assert operation in valid_tag_operations, f'The tag operation submitted was "{operation}" which is invalid.\nValid Tag Operations are: {valid_tag_operations}'

    ops = json.loads('''[
        {
            "op": "",
            "path": "",
            "value": {}
        }
    ]''')
    
    ops[0]['op'] = operation

    tag = tag_cleaner(tag)

    ops[0]['path'] = f'/tags/{tag}'
    
    assert ops[0]['path'] != '/tags/', 'To tag an item the value of the tag may not be empty.'

    return ops


def tag_hostname(operation, tag, query):
    
    ops = build_tag_operation(operation, tag)
    
    hpi= randori_api.HostnamePatchInput(operations=ops, q=query)
    
    try:
    
        api_response = r_api.patch_hostname(hostname_patch_input=hpi)
    
        return api_response
    
    except ApiException as e:
    
        print("Exception when calling DefaultApi->patch_hostname: %s\n" % e)
    

def tag_ip(operation, tag, query):

    ops = build_tag_operation(operation, tag)
    
    ipi= randori_api.IpPatchInput(operations=ops, q=query)
    
    try:
    
        api_response = r_api.patch_ip(ip_patch_input=ipi)
    
        return api_response
    
    except ApiException as e:
    
        print("Exception when calling DefaultApi->patch_ip: %s\n" % e)



def tag_social_entity(operation, tag, query):

    ops = build_tag_operation(operation, tag)
    
    spi= randori_api.SocialEntityPatchInput(operations=ops, q=query)
    
    try:
    
        api_response = r_api.patch_social_entity(social_entity_patch_input=spi)
    
        return api_response
    
    except ApiException as e:
    
        print("Exception when calling DefaultApi->social_entity: %s\n" % e)



def tag_network(operation, tag, query):

    ops = build_tag_operation(operation, tag)
    
    npi= randori_api.NetworkPatchInput(operations=ops, q=query)
    
    try:
    
        api_response = r_api.patch_network(network_patch_input=npi)
    
        return api_response
    
    except ApiException as e:
    
        print("Exception when calling DefaultApi->patch_network: %s\n" % e)


def tag_target(operation, tag, query):

    ops = build_tag_operation(operation, tag)
    
    tpi= randori_api.TargetPatchInput(operations=ops, q=query)
    
    try:
    
        api_response = r_api.patch_target(target_patch_input=tpi)
    
        return api_response
    
    except ApiException as e:
    
        print("Exception when calling DefaultApi->patch_target: %s\n" % e)




def set_hostname_state(query, **kwargs):
    
    # Patching queries throw an error if the query has the "valid" key in it
    # Which queries generated with the jquery querybuilder tool happen to have
    # So delete the key if it exists
    query.pop('valid', None)

    state_dict = {}

    valid_patch_input_names = valid_patch_inputs.keys()

    for arg_name in kwargs:

        assert arg_name in valid_patch_input_names, f'"{arg_name}" is an invalid input argument.\nValid Inputs are: {valid_patch_input_names}'
        
        valid_patch_input_values = valid_patch_inputs[arg_name]

        assert kwargs[arg_name] in valid_patch_input_values, f'"{kwargs[arg_name]}" is an invalid input value.\nValid Inputs are: {valid_patch_input_values}'
        
        state_dict[arg_name] = kwargs[arg_name]
        
        
    hpi = randori_api.HostnamePatchInput(data=state_dict, q=query)

    try:

        api_response = r_api.patch_hostname(hostname_patch_input=hpi)

        return api_response

    except ApiException as e:

        print(f'Exception when calling DefaultApi->patch_hostname:\n{e}')


def set_ip_state(query, **kwargs):
    
    # Patching queries throw an error if the query has the "valid" key in it
    # Which queries generated with the jquery querybuilder tool happen to have
    # So delete the key if it exists
    query.pop('valid', None)

    state_dict = {}

    valid_patch_input_names = valid_patch_inputs.keys()

    for arg_name in kwargs:

        assert arg_name in valid_patch_input_names, f'"{arg_name}" is an invalid input argument.\nValid Inputs are: {valid_patch_input_names}'
        
        valid_patch_input_values = valid_patch_inputs[arg_name]

        assert kwargs[arg_name] in valid_patch_input_values, f'"{kwargs[arg_name]}" is an invalid input value.\nValid Inputs are: {valid_patch_input_values}'
        
        state_dict[arg_name] = kwargs[arg_name]
        
        
    ipi = randori_api.IpPatchInput(data=state_dict, q=query)

    try:

        api_response = r_api.patch_ip(ip_patch_input=ipi)

        return api_response

    except ApiException as e:

        print(f'Exception when calling DefaultApi->patch_ip:\n{e}')



def set_network_state(query, **kwargs):
    
    # Patching queries throw an error if the query has the "valid" key in it
    # Which queries generated with the jquery querybuilder tool happen to have
    # So delete the key if it exists
    query.pop('valid', None)

    state_dict = {}

    valid_patch_input_names = valid_patch_inputs.keys()

    for arg_name in kwargs:

        assert arg_name in valid_patch_input_names, f'"{arg_name}" is an invalid input argument.\nValid Inputs are: {valid_patch_input_names}'
        
        valid_patch_input_values = valid_patch_inputs[arg_name]

        assert kwargs[arg_name] in valid_patch_input_values, f'"{kwargs[arg_name]}" is an invalid input value.\nValid Inputs are: {valid_patch_input_values}'
        
        state_dict[arg_name] = kwargs[arg_name]
        
        
    npi = randori_api.NetworkPatchInput(data=state_dict, q=query)

    try:

        api_response = r_api.patch_network(network_patch_input=npi)

        return api_response

    except ApiException as e:

        print(f'Exception when calling DefaultApi->patch_network:\n{e}')



def set_social_entity_state(query, **kwargs):
    
    # Patching queries throw an error if the query has the "valid" key in it
    # Which queries generated with the jquery querybuilder tool happen to have
    # So delete the key if it exists
    query.pop('valid', None)

    state_dict = {}

    valid_patch_input_names = valid_patch_inputs.keys()

    for arg_name in kwargs:

        assert arg_name in valid_patch_input_names, f'"{arg_name}" is an invalid input argument.\nValid Inputs are: {valid_patch_input_names}'
        
        valid_patch_input_values = valid_patch_inputs[arg_name]

        assert kwargs[arg_name] in valid_patch_input_values, f'"{kwargs[arg_name]}" is an invalid input value.\nValid Inputs are: {valid_patch_input_values}'
        
        state_dict[arg_name] = kwargs[arg_name]
        
        
    spi = randori_api.SocialEntityPatchInput(data=state_dict, q=query)

    try:

        api_response = r_api.patch_social_entity(social_entity_patch_input=spi)

        return api_response

    except ApiException as e:

        print(f'Exception when calling DefaultApi->patch_social_entity:\n{e}')



def set_target_state(query, **kwargs):
    
    # Patching queries throw an error if the query has the "valid" key in it
    # Which queries generated with the jquery querybuilder tool happen to have
    # So delete the key if it exists
    query.pop('valid', None)

    state_dict = {}

    valid_patch_input_names = valid_patch_inputs.keys()

    for arg_name in kwargs:

        assert arg_name in valid_patch_input_names, f'"{arg_name}" is an invalid input argument.\nValid Inputs are: {valid_patch_input_names}'
        
        valid_patch_input_values = valid_patch_inputs[arg_name]

        assert kwargs[arg_name] in valid_patch_input_values, f'"{kwargs[arg_name]}" is an invalid input value.\nValid Inputs are: {valid_patch_input_values}'
        
        state_dict[arg_name] = kwargs[arg_name]
        
        
    tpi = randori_api.TargetPatchInput(data=state_dict, q=query)

    try:

        api_response = r_api.patch_target(target_patch_input=tpi)

        return api_response

    except ApiException as e:

        print(f'Exception when calling DefaultApi->patch_target:\n{e}')

