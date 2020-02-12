import json
import keyring
import os
import sys

# Max string length in a keychain
# https://stackoverflow.com/a/24165635/6178742
# 16,777,110 characters


def get_orgs():
    '''
        Retrieves the list of orgs with api tokens in the Keychain
        Returns a list with org names

        The Keychain is defined in the OS Environment Variable KEYCHAIN_PATH
    '''
    orgs = keyring.get_password('orgs', '')
    
    orgs = json.loads(orgs)
    
    return orgs


orgs = get_orgs()

if not orgs:
    # Keychain does not have an item named 'orgs' so we create one
    #  You need to set the value to an empty python list
    
    print("Orgs item in the Keychain is empty.  Create an orgs item with a password of \"[]\"")
    sys.exit(1)


path = '/Users/bj/.tokens/'

#filename is the name of the org
for filename in os.listdir(path):
    
    # get a list of existing orgs, a list
    existing_orgs = get_orgs()
    
    # add the new org to the list
    existing_orgs.append(filename)

    # dump the list to a string
    updated_orgs = json.dumps(existing_orgs)

    # update the orgs item in the keychain to the new list of orgs
    keyring.set_password('orgs', '', updated_orgs)


    # the org's api token is the content of the file
    with open((path + filename), 'r+') as f:
        for line in f:
            token = line.rstrip('\n').rstrip(',')

    # create a password item with a name of the org
    #  an empty username and a password of the API token
    keyring.set_password(filename, '', token)
    

final_orgs_list = get_orgs()
print(final_org_list)

