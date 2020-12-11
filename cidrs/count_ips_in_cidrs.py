import argparse
from netaddr import *

#f = open("/Users/bj/docs/cust/Marriott/recon_plus/networks.txt", "rb")

parser = argparse.ArgumentParser(description = 'Read a file with CIDR IP Ranges and count how many IPs are in the CIDRs')

optional = parser._action_groups.pop()

required = parser.add_argument_group('required arguments')

required.add_argument("-i", "--input", required=True, help="File with CIDRs")

args = parser.parse_args()

ip_count = 0

with open(args.input, 'r') as f:
    
    for sn in f.readlines():
        
        ip = IPNetwork(sn)
        
        if ip.version == 6:
            
            continue

        ip_count += len(ip)
    
print(ip_count)
