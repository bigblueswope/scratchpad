import argparse
import json
import socket

def resolve_hostnames(infile, resolution, verbose):

    ip_to_hn_dict = {'unresolveable': []}
    
    total_hosts = 0
    
    resolving_hosts = 0

    with open(infile, "r") as ins:
        
        for line in ins:

            hn = line.strip().rstrip(',')
            
            hn = line.split(',')[0].lower().rstrip('\n')
        
            print("Hostname: '%s'" % hn)
            
            total_hosts += 1
            
            try:
                
                ip = socket.gethostbyname(hn)
                
                if ip:
                    print("Entity resolved.")

                    resolving_hosts += 1

                    if resolution:
                        
                        print(hn, ip)
                    
                    else:
                        
                        print(hn)
                    
                    if verbose:
                        
                        try:
                        
                            ip_to_hn_dict[ip].append(hn)

                        except KeyError:
                            
                            ip_to_hn_dict[ip] = [hn]
                
                else:
                    continue
                    
            except socket.gaierror:
                
                ip_to_hn_dict['unresolveable'].append(hn)

    return (total_hosts, resolving_hosts, ip_to_hn_dict)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Script to resolve a text file of hostnames')

    optional = parser._action_groups.pop()

    required = parser.add_argument_group('required arguments')

    required.add_argument("-i", "--input", required=True, help="File with hostnames")

    optional.add_argument("-r", "--resolution", action='store_true', default=False,
        help="If the resolution arg/flag is provided, print the IP with the hostname")
    
    optional.add_argument('-v', '--verbose', action='store_true', default=False,
        help='Print the IP to Hostname Dict')

    parser._action_groups.append(optional)

    args = parser.parse_args()

    (total_hosts, resolving_hosts, ip_to_hn_dict) = resolve_hostnames(args.input, args.resolution, args.verbose)

    print("\n\n################")
    print("Total Hosts Count: %s" % total_hosts)
    print("Resolving Hosts Count: %s" % resolving_hosts)

    print("Results:\n", json.dumps(ip_to_hn_dict, sort_keys = True, indent = 4))


