import csv

cust_network_column = 'network'

cust_networks = []

with open('cust_networks.csv') as csvfile:
    
    reader = csv.DictReader(csvfile, skipinitialspace=True)
        
    for row in reader:

        cust_host = row[cust_network_column]

        if not cust_host in cust_networks:

            cust_networks.append(cust_host)
        



randori_network_column = 'network'

randori_networks = []

with open('randori_networks.csv') as csvfile:

    reader = csv.DictReader(csvfile, skipinitialspace=True)

    for row in reader:

        randori_host = row[randori_network_column]

        if not randori_host in randori_networks:

            randori_networks.append(randori_host)



randori_unique = list( set(randori_networks) - set(cust_networks) )

customer_unique = list( set(cust_networks) - set(randori_networks) )

print('\n')

print(f'Randori Only Networks\n##############\n{randori_unique}\n##############')

print('\n')

print(f'Customer Only Networks\n##############\n{customer_unique}\n##############')
