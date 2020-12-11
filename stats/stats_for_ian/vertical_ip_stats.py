#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This script performs the necessary actions for collecting the latest IP addresses used by Amazon
Web Services, Google Compute, and Microsoft Azure. At the end, all IP addresses are output to
a CloudIPs.txt file. Each range is printed on a new line following a header naming the provider.
As discussed at https://posts.specterops.io/head-in-the-clouds-bd038bb69e48?gi=c33a4e051d6b

Github Link: https://github.com/chrismaddalena/UsefulScripts/blob/master/UpdateCloudIPs.py
"""


from bs4 import BeautifulSoup
import common_functions
import datetime
#import ipaddress
import json
import dns.resolver
import netaddr
import requests
import xml.etree.ElementTree as ET

# Setup the DNS resolver without a short timeout
resolver = dns.resolver.Resolver()
resolver.timeout = 1
resolver.lifetime = 1


# Lists for holding the IP address ranges as they are collected
aws_network_strings = []
azure_network_strings = []
gcp_network_strings = []
o365_network_strings = []

def get_dns_record(domain, record_type):
    """Simple function to get the specified DNS record for the target domain."""
    answer = resolver.query(domain, record_type)
    return answer


# Fetch the JSON for the latest AWS IP ranges
# The addresses listed in the providers' documentation for the latest addresses

aws_uri =  "https://ip-ranges.amazonaws.com/ip-ranges.json"

try:
    aws_json = requests.get(aws_uri).json()
except:
    print("[!] Failed to get the AWS IP addresses!")

if aws_json:
    print("[+] Collected AWS IP ranges last updated on %s" % aws_json['createDate'])

    with open('sources/aws_networks.json', 'w', encoding='utf-8') as f:
        json.dump(aws_json, f, ensure_ascii=False, indent=4)

    for entity in aws_json['prefixes']:

        net = entity['ip_prefix']

        if not net in aws_network_strings:

            aws_network_strings.append(net)

    for entity in aws_json['ipv6_prefixes']:
        
        net = entity['ipv6_prefix']

        if not net in aws_network_strings:
        
            aws_network_strings.append(net)



# Office 365 and Hosted Exchange IPs are not in the "Azure" subnets
#  This means we need some way to parse the following URL and extract networks from it
#  https://docs.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges?view=o365-worldwide


azure_uri = "https://www.microsoft.com/en-us/download/confirmation.aspx?id=41653"

current_azure_networks_source_urls = [
    'https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_20200921.json',
    'https://download.microsoft.com/download/6/4/D/64DB03BF-895B-4173-A8B1-BA4AD5D4DF22/ServiceTags_AzureGovernment_20200921.json',
    'https://download.microsoft.com/download/0/7/6/076274AB-4B0B-4246-A422-4BAF1E03F974/ServiceTags_AzureGermany_20200921.json',
    'https://download.microsoft.com/download/9/D/0/9D03B7E2-4B80-4BF3-9B91-DA8C7D3EE9F9/ServiceTags_China_20200921.json'
]

for url in current_azure_networks_source_urls:

    azure_json = requests.get(url).json()

    fn = 'sources/azure_' + url.split('/')[-1:][0]
    
    with open(fn , 'w', encoding='utf-8') as f:
        json.dump(azure_json, f, ensure_ascii=False, indent=4)
    
    print(f'[+] Collected azure file {fn}')
    
    for service in azure_json['values']:

        for network in service['properties']['addressPrefixes']:
            
            net = network
            
            if not net in azure_network_strings:
                
                azure_network_strings.append(net)

'''
current_o365_networks_source_urls = [
    'https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7',
    'https://endpoints.office.com/endpoints/China?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7',
    'https://endpoints.office.com/endpoints/Germany?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7',
    'https://endpoints.office.com/endpoints/USGOVDoD?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7',
    'https://endpoints.office.com/endpoints/USGOVGCCHigh?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7'
]
'''

current_o365_networks_source_urls = [
    'https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7',
]

for url in current_o365_networks_source_urls:

    o365_json = requests.get(url).json()

    fn = 'sources/o365_' + url.split('/')[-1:][0].split('?')[:1][0] + '.json'

    with open(fn, 'w', encoding='utf-8') as f:
        json.dump(o365_json, f, ensure_ascii=False, indent=4)

    print(f'[+] Collected o365 file {fn}')
    

    for entity in o365_json:

        try:

            for network in entity['ips']:
                
                net = network
                
                if not net in o365_network_strings:
                    
                    o365_network_strings.append(net)
        
        except KeyError:
            
            pass




# Begin the TXT record collection for Google Compute
# First, the hostnames must be collected from the primary _cloud-netblocks subdomain

gcp_netblock_spf_seed = "_cloud-netblocks.googleusercontent.com"

gcp_netblock_spf_hostnames = []

try:
    txt_records = get_dns_record(gcp_netblock_spf_seed, "TXT")

    for rdata in txt_records.response.answer:

        for item in rdata.items:

            for member in item.to_text().split(' ',):

                try:
                    member_name, member_value = member.split(':',)
                except:
                    continue

                if (member_name == 'include' and member_value):

                    gcp_netblock_spf_hostnames.append(member_value)

except Exception as e:
    print(e)
    pass

    


# Now the TXT records of each of the netblocks subdomains must be collected

# Google publishes these networks as spf records and spf records can be recursive
#  Because we do not know if a record will contain a pointer to an additional record
#  we iterate over the list and if we find a pointer to an additional record
#  append the record to the list and the while loop will notice that the list is longer
#  and it will continue to iterate over the additional list members.

i = 0

while i < len(gcp_netblock_spf_hostnames):

    hostname = gcp_netblock_spf_hostnames[i]

    print(f'[+] Collecting TXT records for {hostname}')

    txt_records = get_dns_record(hostname, "TXT")

    txt_entries = []

    for rdata in txt_records.response.answer:

        for item in rdata.items:

            for member in item.to_text().split(' ',):

                #only split one time so we do not split IPv6 addresses
                try:
                    member_name, member_value = member.split(':', 1)
                except:
                    continue

                if (member_name == 'include' and member_value):
                    # This is entry is a pointer to another record so append it to the list of records we must resovle

                    if not member_value in gcp_netblock_spf_hostnames:

                        gcp_netblock_spf_hostnames.append(member_value)

                elif member_name in ('ip4' ,'ip6'):

                    if not member_value in gcp_network_strings:

                        gcp_network_strings.append(member_value)

    i += 1


fn = 'sources/gcp_networks.json'

with open(fn, 'w', encoding='utf-8') as f:
    json.dump(gcp_network_strings, f, ensure_ascii=False, indent=4)




print('Building aws_networks')
aws_networks = []
for network in map(netaddr.IPNetwork, aws_network_strings):
    aws_networks.append(network)

print('Building azure_networks')
azure_networks = []
for network in map(netaddr.IPNetwork, azure_network_strings):
    azure_networks.append(network)

print('Building gcp_networks')
gcp_networks = []
for network in map(netaddr.IPNetwork, gcp_network_strings):
    gcp_networks.append(network)

print('Building o365_networks')
o365_networks = []
for network in map(netaddr.IPNetwork, o365_network_strings):
    o365_networks.append(network)




def analyze_ips(ip_strs, org_id):
    
    results = {
        'org_id' : org_id,
        'total_ip_count' : 0,
        'on_prem_ipv4_count' : 0,
        'cloud_ipv4_count' : 0,
        'amazon_ipv4_count' : 0,
        'azure_ipv4_count' : 0,
        'o365_ipv4_count' : 0,
        'gcp_ipv4_count' : 0,
        'private_ipv4_count' : 0,
        'on_prem_ipv6_count' : 0,
        'cloud_ipv6_count' : 0,
        'amazon_ipv6_count' : 0,
        'azure_ipv6_count' : 0,
        'o365_ipv6_count' : 0,
        'gcp_ipv6_count' : 0,
        'private_ipv6_count' : 0,
        'invalid_ip_count' : 0,
    }
    
    
    results['total_ip_count'] += len(ip_strs)
    
    ips = []
    
    for ip_str in ip_strs:
        
        try:
            
            #i = ipaddress.ip_address(ip_str)
            ip = netaddr.IPAddress(ip_str)

            #if ( i.is_reserved or i.is_loopback or i.is_private or i.is_multicast or i.is_link_local ):
            if any( [ ip.is_private(), ip.is_reserved(), ip.is_loopback() ] ):
                
                if ip.version == 4:
                    results['private_ipv4_count'] += 1
                else:
                    results['private_ipv6_count'] += 1
    
            else:
    
                ips.append(ip)
                    
        except ValueError as e:
            
            results['invalid_ip_count'] += 1
    
    
    
    for ip in ips:
    
        check_next_ip = False

        for aws_network in aws_networks:
            if ip in aws_network:
                check_next_ip = True
                if ip.version == 4:
                    results['cloud_ipv4_count'] += 1
                    results['amazon_ipv4_count'] += 1
                    continue
                else:
                    results['cloud_ipv6_count'] += 1
                    results['amazon_ipv6_count'] += 1
                    continue
    
        if check_next_ip:
            continue
        
        for gcp_network in gcp_networks:
            if ip in gcp_network:
                check_next_ip = True
                if ip.version == 4:
                    results['cloud_ipv4_count'] += 1
                    results['gcp_ipv4_count'] += 1
                    continue
                else:
                    results['cloud_ipv6_count'] += 1
                    results['gcp_ipv6_count'] += 1
                    continue

    
        if check_next_ip:
            continue
    
        for azure_network in azure_networks:
            if ip in azure_network:
                check_next_ip = True
                if ip.version == 4:
                    results['cloud_ipv4_count'] += 1
                    results['azure_ipv4_count'] += 1
                    continue
                else:
                    results['cloud_ipv6_count'] += 1
                    results['azure_ipv6_count'] += 1
                    continue
    
        if check_next_ip:
            continue
    
        for o365_network in o365_networks:
            if ip in o365_network:
                check_next_ip = True
                if ip.version == 4:
                    results['cloud_ipv4_count'] += 1
                    results['o365_ipv4_count'] +=1
                    continue
                else:
                    results['cloud_ipv6_count'] += 1
                    results['o365_ipv6_count'] +=1
                    continue
        
        if check_next_ip:
            continue
    
        if ip.version == 4:
            results['on_prem_ipv4_count'] += 1
        else:
            results['on_prem_ipv6_count'] += 1
    
    
    return results
    



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

    with open('vertical_lists/hc_orgs.json') as f:
        orgs = json.load(f)['orgs']

    all_org_ip_breakdowns = []

    for org_name in common_functions.get_orgs():

        print(org_name)

        common_functions.configuration.access_token = common_functions.get_api_token(org_name);

        ip_strs = []

        org_ips = common_functions.get_ips(initial_query)

        org_id = org_ips[0].org_id

        if not org_id in orgs:
            continue

        for entity in org_ips:
            ip_strs.append(entity.ip)

        ip_breakdown = analyze_ips(ip_strs, org_id)

        print(ip_breakdown)

        all_org_ip_breakdowns.append(ip_breakdown.copy())


    td = datetime.datetime.today().strftime('%Y-%m-%d')

    filename = f'results/vertical_cloud_ip_stats_{td}.csv'

    with open(filename, 'w') as file:

        header = ','.join(all_org_ip_breakdowns[0].keys())

        file.write(header)
        file.write('\n')
        print(header)

        for each_org in all_org_ip_breakdowns:

            temp_list = []

            for value in each_org.values():

                temp_list.append(str(value))

            line = ','.join(temp_list)

            file.write(line)
            file.write('\n')
            print(line)

