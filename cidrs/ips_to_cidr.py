import argparse
import ipaddress

import common_functions


ipv4_list = []
ipv6_list = []


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Read a file with IP addresses and convert them into CIDR IP Ranges')

    optional = parser._action_groups.pop()

    required = parser.add_argument_group('required arguments')

    required.add_argument("-i", "--input", required=True, help="File with IP Addresses")

    args = parser.parse_args()


    with open(args.input, 'r') as file:

       for line in file:

            line = common_functions.line_cleaner(line)
            
            if not line:
                continue
            
            try:
                ret = ipaddress.ip_address(str(line))

                if isinstance(ret, ipaddress.IPv4Address):

                    ipv4_list.append(ret)

                elif isinstance(ret, ipaddress.IPv6Address):
                    
                    ipv6_list.append(ret)

                else:

                    raise TypeError("ip_address returns unknown type? {0}".format(str(ret)))

            except ValueError:

                print("%s is not a valid IP Address" % line)

                pass

    
    ipv4_cidrs = ipaddress.collapse_addresses(ipv4_list)
    
    for foo in ipv4_cidrs:

        print(str(foo.network_address) + '/' + str(foo._prefixlen))


    
    ipv6_cidrs = ipaddress.collapse_addresses(ipv6_list)
    
    for foo in ipv6_cidrs:

        print(str(foo.network_address) + '/' + str(foo._prefixlen))
    
