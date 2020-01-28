import argparse
import socket

def resolve_hostnames(input, resolution):
    resolving_hosts = []
    with open(input, "r") as ins:
        for line in ins:
            hn = line.strip().rstrip('\n').rstrip(',')
            try:
                ip = socket.gethostbyname(hn)
                if ip:
                    if resolution:
                        print(hn, ip)
                    else:
                        print(hn)
                else:
                    continue
            except socket.gaierror:
                continue

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Script to resolve a text file of hostnames')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, help="File with hostnames")
    optional.add_argument("-r", "--resolution", action='store_true', default=False,
        help="If the resolution arg/flag is provided, print the IP with the hostname")
    parser._action_groups.append(optional)
    args = parser.parse_args()

    resolve_hostnames(args.input, args.resolution)

