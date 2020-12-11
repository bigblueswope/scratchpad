from netaddr import IPNetwork, IPAddress

list_of_ip_address = ['3.229.72.71', '54.208.9.110', '2600:1f18:6670:ad00:3dbe:48d3:1cb6:e81b', '162.217.252.55']

list_of_subnets = [
    "2600:1f11::/36",
    "2600:1f12::/36",
    "2600:1f13::/36",
    "2600:1f14:7ff:f800::/53",
    "2600:1f14::/35",
    "2600:1f14:fff:f800::/53",
    "2600:1f15::/32",
    "2600:1f16::/36",
    "2600:1f18:3fff:f800::/53",
    "2600:1f18:7fff:f800::/53",
    "2600:1f18::/33",
    "2600:1f1c:7ff:f800::/53",
    "2600:1f1c::/36",
    "2600:1f1c:fff:f800::/53",
    "2600:1f1e:7ff:f800::/53",
    "2600:1f1e::/36",
    "2600:1f1e:fff:f800::/53",
    "2600:1f1f::/36"
]


l_ip_address = []

for ip in map(IPAddress, list_of_ip_address):
    l_ip_address.append(ip)

l_ip_subnet = []

for net in map(IPNetwork, list_of_subnets):
    l_ip_subnet.append(net)

cloud_ip_count = 0
non_cloud_ip_count = 0

for ip in l_ip_address:
    print(f'IP: {str(ip)}')
    check_next = False
    for network in l_ip_subnet:
        print(str(network))
        if ip in network:
            cloud_ip_count += 1
            check_next = True

        if check_next:
            continue
'''
if any(x in y for x in l_ip_address for y in l_ip_subnet):
    cloud_ip_count += 1
else:
    non_cloud_ip_count += 1
'''


print(f'Cloud IP Count: {cloud_ip_count}')
print(f'Non-Cloud IP Count: {non_cloud_ip_count}')
