import argparse
import socket

def resolve_hostnames(infile, resolution):
    
    total_hosts = 0
    
    resolving_hosts = 0

    with open(infile, "r") as ins:
        
        for line in ins:

            hn = line.strip().rstrip('\n').rstrip(',')
        
            total_hosts += 1
            
            try:
                
                ip = socket.gethostbyname(hn)
                
                if ip:

                    resolving_hosts += 1

                    if resolution:
                        
                        print(hn, ip)
                    
                    else:
                        
                        print(hn)
                
                else:
                    
                    continue
            
            except socket.gaierror:
                
                continue

    return (total_hosts, resolving_hosts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Script to resolve a text file of hostnames')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, help="File with hostnames")
    optional.add_argument("-r", "--resolution", action='store_true', default=False,
        help="If the resolution arg/flag is provided, print the IP with the hostname")
    parser._action_groups.append(optional)
    args = parser.parse_args()

    (total_hosts, resolving_hosts) = resolve_hostnames(args.input, args.resolution)

    print("\n\n################")
    print("Total Hosts: %s" % total_hosts)
    print("Resolving Hosts: %s" % resovling_hosts)


