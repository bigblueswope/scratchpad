import getpass
import json
import keyring
import os
import platform
import sys

# Max string length in a keychain
# https://stackoverflow.com/a/24165635/6178742
# 16,777,110 characters

if platform.system() == 'Darwin':

    keychain_file = os.environ.get('KEYCHAIN_PATH')

    assert keychain_file, "OS Environment Variable 'KEYCHAIN_PATH' is not defined"


def get_orgs():
    '''
        Retrieves the list of orgs with api tokens in the Keychain
        
        The Keychain is defined in the OS Environment Variable KEYCHAIN_PATH
        
        Returns a sorted list with org names
    '''
    orgs = keyring.get_password('orgs', '')
    
    orgs = json.loads(orgs)

    orgs = sorted(orgs)
    
    return orgs



def print_orgs():

    orgs = get_orgs()

    if not orgs:

        print("Keychain %s did not contain an item called 'orgs'" % keychain_file)

        print("Call the function initialize_orgs() to initialize the Keychain")
        
        sys.exit(1)
        
    else:
        for org in orgs:
            print(org)



def get_api_token(org_name):

    if not org_name:

        org_name = input("Org Name: ")
    

    if not org_name == 'orgs':

        assert org_name in get_orgs(), "%s is not in the list of orgs in the Keychain" % org_name

    token = keyring.get_password(org_name, '')
    
    return token




def set_api_token(org_name, token_value=None):

    if not org_name:

        org_name = input("Org Name: ")

    
    if not token_value:

        token_value = getpass.getpass()

        assert token_value, "No token passed into function and no token value provided at prompt"
   

    # keyring.set_password will update an existing item
    #   or create an item if it does not exist
    keyring.set_password(org_name, '', token_value)

    existing_orgs = get_orgs()

    if not org_name in existing_orgs and not org_name == 'orgs':
        
        existing_orgs.append(org_name)
        
        updated_orgs = json.dumps(existing_orgs)
        
        keyring.set_password('orgs', '', updated_orgs)
 



def delete_api_token(org_name):
    
    try:
        
        keyring.delete_password(org_name, '')

    except keyring.errors.PasswordDeleteError:
        
        pass


    existing_orgs = get_orgs()

    if org_name in existing_orgs:
        
        existing_orgs.remove(org_name)

        updated_orgs = json.dumps(existing_orgs)
        
        keyring.set_password('orgs', '', updated_orgs)
 



def initialize_orgs():

    orgs = get_orgs()

    if orgs:
        
        print("Keychain already contains an 'orgs' item. We will not overwrite the existing item.")

        sys.exit(1)

    else:

        set_api_token('orgs', '[]')



