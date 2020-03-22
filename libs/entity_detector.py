import datetime
import os
import argparse
import ipaddress
import sys

import tldextract

from urllib.parse import urlparse

import common_functions


# tldextract uses .tld_set to validate TLDs
# to ensure we are using an up to date copy
# delete the file if it is older than 7 days
# and call update

#seven days ago
sda = datetime.date.today() - datetime.timedelta(7)

#seven days ago as unixtimestamp
sda = sda.strftime("%s")

tld_set_file = os.path.join(tldextract.__path__[0], '.tld_set')

try:
    tld_set_date = os.path.getmtime(tld_set_file)

    if int(tld_set_date) < int(sda):
        os.remove(tld_set_file)

except FileNotFoundError:
    pass

tldextract.TLDExtract(include_psl_private_domains=False).update(True)



def get_domain(i):
    try:
        ext = tldextract.extract(i)

        domain = '.'.join((ext.domain, ext.suffix))

    except Exception as e:
        print(str(e))

    return domain



def detect_entity(i):

    try:
        # creates a list with each portion of the name a distinct entry
        ext = tldextract.extract(i)
        
        # rebuilds the list while stripping any trailing dots
        fqdn = '.'.join(ext).strip('.')

        domain = get_domain(i)

        # ext.suffix may be more than just one word
        #   example:  co.uk is 2 part suffix
        #   tldextract is smart enough to treat it properly

        if ext.subdomain and ext.suffix:
            # Finds FQDNs
            return ('hostnames', fqdn, domain)

    
        # we did not have a subdomain extracted so this is not a FQDN
        #   so verify that we got a domain portion and it isn't just a TLD

        elif ext.domain and ext.suffix:
            # Finds Domains
            return ('domains', fqdn, domain)

        # the line was not a domain nor a FQDN
        else:
            o = urlparse(i)[1]

            if o:
                i = o

            try:
                try:
                    i = int(i)
                except ValueError as e:
                    pass
                
                i = ipaddress.ip_address(i)
                
                if ( i.is_reserved
                    or i.is_loopback 
                    or i.is_private
                    or i.is_multicast
                    or i.is_link_local ):
                
                    return ('reserved_ips', str(i), None)
                
                else:
                    return ('ips', str(i), None)
                
            except ValueError as e:
                pass
            
            try:
                ipaddress.ip_network(i)
            
                return ('networks', str(i), None)

            except ValueError as e:
                pass

        #########################
        # String provided does no match an entity we support
        return ('unsupported', i, None)
        
    except Exception as e: 
        print(e)
        sys.exit(1)
        


        
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description = 
        "Script to separate hostnames, domains, IPs, and Networks from a file.")

    required = parser.add_argument_group('required arguments')

    required.add_argument("-i", "--input", required=True, help="File containing entities to separate.")

    args = parser.parse_args()

    ent_dict = {
        'hostnames' : [],
        'domains' : [],
        'ips' : [],
        'networks' : [],
        'reserved_ips' : [], 
        'unsupported' : []
    }

    with open(args.input, 'r+') as fn:

        entities = fn.readlines()

    for i in entities:

        i = common_functions.line_cleaner(i)

        if not i:
            continue
        
        entity_type, entity, _ = detect_entity(i)

        ent_dict[entity_type].append(entity)
        
    
    for k,v in ent_dict.items():
        print(k.capitalize(), ':\n', v, '\n\n')
    
