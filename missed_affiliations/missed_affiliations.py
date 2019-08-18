import datetime
import os
import argparse
import sys
import tldextract
import logging
import logging.config
import socket
import json
import csv
import requests

def refresh_tld_set(sda):

    # tldextract uses .tld_set to validate TLDs
    # tldextract will download a new one if it is missing
    # to ensure we are using an up to date copy
    # delete the file if it is older than 7 days
    tld_path = tldextract.__file__

    tld_path= '/'.join(tld_path.split('/')[:-1])

    tld_set_file = tld_path + "/.tld_set"

    tld_set_date = os.path.getmtime(tld_set_file)
    
    logger.info('Checking .tld_set age')

    if tld_set_date < sda:
        os.remove(tld_set_file)
        logger.info('.tld_set age older than 7 days. Refreshing .tld_set')


def get_user_response():
    # Yes No or Possibly
    ur = input("Domain appears to belong to Org? (y/n/p/i/?): ")

    if ur == '?':
        print("Possible Responses:\
        \n\ty: Yes \
        \n\tn: No \
        \n\tp: Possibly \
        \n\ti: Yes and Insert Org Name into list of auto-matching Org Names \
        \n\t?: Prints this info")
        ur = get_user_response()

    if ur not in ('y', 'n', 'p', 'i', 'Y', 'N', 'P', 'i'):
        ur = get_user_response()
    return ur


def get_api_key():
    # Get the whoisxmlapi token from environment variables
    apikey = os.getenv("WHOISXMLAPI_TOKEN")
    
    if apikey is None:
        raise ValueError("Missing environment variable WHOISXMLAPI_TOKEN.")

    elif len(apikey) < 32:
        raise ValueError("This token appears too short. \
            Please ensure the entire token \
            is added as an environment variable.")
    
    return apikey


def get_history_api_key():
    # Get the whoisxmlapi history token from environment variables
    history_apikey = os.getenv("WHOISXMLAPI_HISTORY_TOKEN")
    
    if history_apikey is None:
        raise ValueError("Missing environment variable WHOISXMLAPI_HISTORY_TOKEN.")
    
    elif len(history_apikey) < 32:
        raise ValueError("This token appears too short. \
            Please ensure the entire token \
            is added as an environment variable.")
    
    return history_apikey


def get_whois_for_domain(apikey, domain):
    p = {"apiKey": apikey,
         "outputFormat": "json",
         'domainName': domain,
         'checkProxyData': 1}
    r = requests.get("https://www.whoisxmlapi.com/whoisserver/WhoisService", params=p)
    j = r.json()
    return j


def get_whois_for_domain_history(history_apikey, domain):
    p = {"apiKey": history_apikey,
         "outputFormat": "json",
         "mode": "purchase",
         'domainName': domain}
    r = requests.get("https://whois-history-api.whoisxmlapi.com/api/v1", params=p)
    j = r.json()
    return j


def lookup_whois(apikey, domain):

    out_file = 'output/whois/%s.json' % domain 

    if not (os.path.exists(out_file) and os.path.getsize(out_file) > 0):

        with open(out_file, 'w+') as res_out:

            res_whois = get_whois_for_domain(apikey, domain)

            res_out.write(json.dumps(res_whois, indent=4, sort_keys=True))

    return out_file


def lookup_whois_history(history_apikey, domain):
    out_file = 'output/whois_history/%s.json' % domain

    if not (os.path.exists(out_file) and os.path.getsize(out_file) > 0):

        with open(out_file, 'w+') as res_out:

            res_whois = get_whois_for_domain_history(history_apikey, domain)

            res_out.write(json.dumps(res_whois, indent=4, sort_keys=True))

    return out_file



def analyze_results(fn, org_names):
    with open(fn, 'r') as f:
        dom_json = json.load(f)

    whois_dict = dom_json['WhoisRecord']

    try:
        reg_org = whois_dict['registrant']['organization']
        print ("Registrant Organization:", reg_org)
    except:
        try:
            reg_org = whois_dict['registryData']['registrant']['organization']
            print ("Registrant Organization:", reg_org)
        except:
            reg_org = ''
            pass

    try:
        reg_name = whois_dict['registrant']['name']
        print ("Registrant Name:", reg_name)
    except:
        try:
            reg_name = whois_dict['registryData']['registrant']['name']
            print ("Registrant Name:", reg_name)
        except:
            reg_name = ''
            pass

    try:
        contact_email = whois_dict['contactEmail']
        print("Contact Email:", contact_email)
    except:
        contact_email = ''
        pass

    try:
        admin_contact = whois_dict['administrativeContact']
    except:
        try:
            admin_contact = whois_dict['administrativeContact']
            print ("Admin Contact:", admin_contact)
        except:
            admin_contact = ''
            pass

    try:
        tech_contact = whois_dict['technicalContact']
        print ("Tech Contact:", tech_contact)
    except:
        try:
            tech_contact = whois_dict['registryData']['technicalContact']
            print ("Tech Contact:", tech_contact)
        except:
            tech_contact = ''
            pass

    try:
        domain = whois_dict['domainName']
        print ("Domain Name:", domain)
    except:
        try:
            domain = whois_dict['registryData']['domainName']
            print ("Domain Name:", domain)
        except:
            domain = '.'.join(fn.split('/')[-1].split('.')[:-1])
            print ("Domain Name:", domain)

    try:
        name_servers = whois_dict['nameServers']['rawText']
        print ("Name Servers:", name_servers)
    except:
        try:
            name_servers = whois_dict['registryData']['nameServers']['rawText']
            print ("Name Servers:", name_servers)
        except:
            try:
                name_servers = whois_dict['nameServers']
                print ("Name Servers:", name_servers)
            except:
                name_servers = ''
                pass
    
    if len(reg_org) and reg_org in org_names:
        print("@@@@@@ Domain Registrant ORG Matched Other Verified Registrant Orgs")
        print("@@@@@@ Automatically verified", domain)
        return (domain, 'a')

    if len(reg_name) and reg_name in org_names:
        print("@@@@@@ Domain Registrant NAME Matched Other Verified Registrant Orgs")
        print("@@@@@@ Automatically verified", domain)
        return (domain, 'a')

    ur = get_user_response()

    if ur in ('i', 'I') and len(reg_org):
        org_names.append(reg_org)

    if ur in ('p', 'P'):
        whois_hist_file = lookup_whois_history(history_apikey, domain)
       
        with open(whois_hist_file, 'r') as f:
            history = json.load(f)

        print(json.dumps(history, indent=4, sort_keys=True))
        
        print("\n\n****", domain)
    
        ur = get_user_response()

    return (domain, ur)


def main():
    dom_results = {}
    org_names = []

    hosts_out = open('output/hosts.txt', 'w+')
    domains_out = open('output/domains.txt', 'w+')
    ips_out = open('output/ips.txt', 'w+')
    no_match_out = open('output/no_match.txt', 'w+')

    with open(args.input, 'r+') as fn:
        doms = fn.read()
        fn.close()

    dom_list = doms.splitlines()

    dom_list_len = len(dom_list)
    
    counter = 1

    for i in dom_list:

        print("\n\n\nProcessing %i of %i" % (counter, dom_list_len))

        try:
            # Finds IP Addresses
            socket.inet_aton(i)

            logger.info("IP: %s",i)
            
            print("IP:", i)
            
            dom_results[i] = 'i'

            ips_out.write(i + '\n')
        
        except OSError as e:
        
            i = i.lower()
            
            ext = tldextract.extract(i)
            
            res = '.'.join(ext).strip('.')
            
            if ext.subdomain and ext.suffix:
                # Finds FQDNs
                logger.info("Host: %s", res)
        
                print ("Host:", res)

                dom_results[res] = 'h'
        
                hosts_out.write(res + '\n')
        
            elif ext.domain and ext.suffix:
                # Finds Domains
                logger.info("Domain: %s", res)
                
                print("#" * 80)

                print ("Domain:", res)
        
                domains_out.write(res + '\n')
            
                if args.whois:
                    whois_results_file = lookup_whois(apikey, res)

                    dom,ur = analyze_results(whois_results_file, org_names)

                    dom_results[dom] = ur
                else:
                    dom_results[res] = 'z'
                    
            else:
                try:
                    # trying inet_aton again just in case we had a URL that
                    # had an IP instead of a FQDN in it
                    # Finds IPs that were part of URL
                    socket.inet_aton(ext.domain)
        
                    logger.info("IP: %s", ext.domain)
        
                    print("IP:", ext.domain)

                    dom_results[ext.domain] = 'i'
        
                    ips_out.write(ext.domain + '\n')
        
                except:
                    # String provided does no match an entity we support
                    logger.warning("No Match: %s", res)
        
                    print("No Match: ", res)

                    dom_results[res] = 'n'
        
                    no_match_out.write(res +'\n')

        counter+=1
        
    out_fn = '.'.join(args.input.split('/')[-1].split('.')[:-1])
        
    out_fn = "output/" + out_fn + ".csv"

    with open(out_fn, 'w+') as f:
        w = csv.writer(f)
        w.writerows(dom_results.items())

    hosts_out.close()
    domains_out.close()
    ips_out.close()
    
    print("\n\n\n\n" + "*" * 120)
    print("Check output directory for lists of hosts, domains, IPs and unknown entities")
    print("%s contains the list of domains and whether they belong to the Org or not" % (out_fn))
    print("*" * 120)


if __name__ == "__main__":
    
    if not (os.path.isdir("output")):
        os.mkdir("output")

    if not (os.path.isdir("output/whois")):
        os.mkdir("output/whois")

    if not (os.path.isdir("output/whois_history")):
        os.mkdir("output/whois_history")
    
    #seven days ago
    sda = datetime.date.today() - datetime.timedelta(7)

    #seven days ago as unixtimestamp
    sda = sda.strftime("%s")

    parser = argparse.ArgumentParser(description = 
        "Script to separate hostnames, domains and IPs \
        from one file into 3 distinct files and optionally\
        verify domain ownership utilizting whoisxmlapi data.")
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, help="File containing entities to separate.")
    optional.add_argument("-w", "--whois", default=False, action="store_true",
        help="If the whois arg/flag is provided, perform whois lookups for \
                domains using whoisxmlapi")
    parser._action_groups.append(optional)

    args = parser.parse_args()

    if not args.input:
        print("No input file defined.  Rerun the script with -i <input_file_name>")
        sys.exit(1)
    
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger(__name__)
    logger.info("Entity Separation Started")
    
    if args.whois:
        logger.info("Whois Lookups Enabled")
        apikey = get_api_key()
        history_apikey = get_history_api_key()
        refresh_tld_set(sda)


    main()

