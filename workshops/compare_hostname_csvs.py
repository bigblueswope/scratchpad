import csv

cust_hostname_column = 'hostname'

cust_hostnames = []

with open('avista/External Scans.txt') as csvfile:
    
    reader = csv.DictReader(csvfile, skipinitialspace=True)
        
    for row in reader:

        cust_host = row[cust_hostname_column]

        if not cust_host in cust_hostnames:

            cust_hostnames.append(cust_host)
        



randori_hostname_column = 'hostname'

randori_hostnames = []

with open('avista/randori_hostnames.csv') as csvfile:

    reader = csv.DictReader(csvfile, skipinitialspace=True)

    for row in reader:

        randori_host = row[randori_hostname_column]

        if not randori_host in randori_hostnames:

            randori_hostnames.append(randori_host)



randori_unique = list( set(randori_hostnames) - set(cust_hostnames) )

customer_unique = list( set(cust_hostnames) - set(randori_hostnames) )

print('\n')

print(f'Randori Only Hostnames\n##############\n{randori_unique}\n##############')

print('\n')

print(f'Customer Only Hostnames\n##############\n{customer_unique}\n##############')
