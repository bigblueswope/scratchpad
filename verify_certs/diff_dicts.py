
platform_cert_tags = {'a':1, 'b':2}
connection_cert_tags = {'a':2, 'b':2}

plat_cert_tags_set = set(platform_cert_tags.items())

conn_cert_tags_set = set(connection_cert_tags.items())

print('Platform Certs Tags:', plat_cert_tags_set)
print()
print('Connection Cert Tags:', conn_cert_tags_set)
print()

platform_only_tags =  list( plat_cert_tags_set - conn_cert_tags_set )

print('Platform Only Tags:', platform_only_tags)
print()

''' 
for each_tuple in platform_only_tags:
    remove_tag(each_tuple)
'''

connection_only_tags = list( conn_cert_tags_set - plat_cert_tags_set )

print('Connection only tags:', connection_only_tags)
print()

'''
for each_tuple in conn_only_tags:
    add_tag(each_tuple)
'''
