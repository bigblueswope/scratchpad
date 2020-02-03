import datetime
import os
import argparse
import ipaddress
import sys

import tldextract

from urllib.parse import urlparse

def refresh_tld_set():

    # tldextract uses .tld_set to validate TLDs
    # tldextract will download a new one if it is missing
    # to ensure we are using an up to date copy
    # delete the file if it is older than 7 days
    
    #seven days ago
    sda = datetime.date.today() - datetime.timedelta(7)

    #seven days ago as unixtimestamp
    sda = sda.strftime("%s")

    tld_path = tldextract.__file__

    tld_path= '/'.join(tld_path.split('/')[:-1])

    tld_set_file = tld_path + "/.tld_set"

    tld_set_date = os.path.getmtime(tld_set_file)
    
    if int(tld_set_date) < int(sda):
        os.remove(tld_set_file)


def detect_entities(src_file):

    hosts = []
    domains = []
    reserved_ips = []
    ips = []
    networks = []
    unsupported = []

    refresh_tld_set()

    with open(src_file, 'r+') as fn:
        entities = fn.read()

    entities_list = entities.splitlines()

    dl = len(entities_list)
    
    counter = 0

    for i in entities_list:

        counter+=1
        
        if ',' in i:
            #assumes domain/host is first entry in a CSV
            i = i.split(',')[0]

        if '#' in i:
            # Treating # as an in-line comment so split on # for the first field
            i = i.split('#')[0]

        i = i.lower().strip(' ,.')

        if ( i == 'domainname'):
            # Skip line with value of "domainname"
            #print("\nProssesing header line %i of %i. Skipping" % (counter, dl))
            continue

        if not i:
            # Skip empty lines
            #print("\nProcessing empty line %i of %i.  Skipping" % (counter, dl))
            continue

        #print("\nProcessing %s: %i of %i" % (i, counter, dl))

        try:
            # creates a list with each portion of the name a distinct entry
            ext = tldextract.extract(i)
            
            # rebuilds the list while stripping any trailing dots
            res = '.'.join(ext).strip('.')
            
            # ext.suffix may be more than just one word
            #   example:  co.uk is 2 part suffix
            #   tldextract is smart enough to treat it properly
            if ext.subdomain and ext.suffix:
                # Finds FQDNs
                hosts.append(res)
                continue
        
            # we did not have a subdomain extracted so this is not a FQDN
            #   so verify that we got a domain portion and it isn't just a TLD
            elif ext.domain and ext.suffix:
                # Finds Domains
                domains.append(res)
                continue

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
                    
                        reserved_ips.append(str(i))
                        continue
                    
                    ips.append(str(i))
                    continue
                    
                except ValueError as e:
                    pass
                
                try:
                    ipaddress.ip_network(i)
                
                    networks.append(i)
                    continue

                except ValueError as e:
                    pass

            #########################
            # String provided does no match an entity we support
            unsupported.append(i)
            continue
            
        except Exception as e: 
            print(e)
            sys.exit(1)
        
    return (hosts, domains, ips, networks, reserved_ips, unsupported)


        
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description = 
        "Script to separate hostnames, domains, IPs, and Networks from a file.")
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, help="File containing entities to separate.")

    args = parser.parse_args()

    src_file = args.input

    entity_types = detect_entities(src_file)

    for entity_type in entity_types:
        print(entity_type)



