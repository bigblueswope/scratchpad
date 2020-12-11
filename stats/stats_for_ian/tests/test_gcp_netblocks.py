import dns.resolver
import sys


# Setup the DNS resolver without a short timeout
resolver = dns.resolver.Resolver()
resolver.timeout = 1
resolver.lifetime = 1



def get_dns_record(domain, record_type):
    """Simple function to get the specified DNS record for the target domain."""
    answer = resolver.query(domain, record_type)
    return answer



# Begin the TXT record collection for Google Compute
# First, the hostnames must be collected from the primary _cloud-netblocks subdomain

gcp_netblock_spf_seed = "_cloud-netblocks.googleusercontent.com"

gcp_netblock_names = []

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
                    
                    gcp_netblock_names.append(member_value)

except Exception as e:
    print(e)
    pass



gcp_network_strings = []

# Now the TXT records of each of the netblocks subdomains must be collected

# Google publishes these networks as spf records and spf records can be recursive
#  Because we do not know if a record will contain a pointer to an additional record
#  we iterate over the list and if we find a pointer to an additional record
#  append the record to the list and the while loop will notice that the list is longer
#  and it will continue to iterate over the additional list members.

i = 0

while i < len(gcp_netblock_names):

    hostname = gcp_netblock_names[i]
    
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
                
                if member_name == 'include':
                    # This is entry is a pointer to another record so append it to the list of records we must resovle

                    if not member_value in gcp_netblock_names:
                        
                        gcp_netblock_names.append(member_value)

                elif member_name in ('ip4' ,'ip6'):
                    
                    if not member_value in gcp_network_strings:
                        
                        gcp_network_strings.append(member_value)
    
    i += 1
    

print(gcp_network_strings)
