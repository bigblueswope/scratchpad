import csv

cust_ip_column = 'ip'

cust_ips = []

with open('cust_ips.csv') as csvfile:
    
    reader = csv.DictReader(csvfile, skipinitialspace=True)
        
    for row in reader:

        cust_host = row[cust_ip_column]

        if not cust_host in cust_ips:

            cust_ips.append(cust_host)
        



randori_ip_column = 'ip'

randori_ips = []

with open('randori_ips.csv') as csvfile:

    reader = csv.DictReader(csvfile, skipinitialspace=True)

    for row in reader:

        randori_host = row[randori_ip_column]

        if not randori_host in randori_ips:

            randori_ips.append(randori_host)



randori_unique = list( set(randori_ips) - set(cust_ips) )

customer_unique = list( set(cust_ips) - set(randori_ips) )

print('\n')

print(f'Randori Only Ips\n##############\n{randori_unique}\n##############')

print('\n')

print(f'Customer Only Ips\n##############\n{customer_unique}\n##############')
