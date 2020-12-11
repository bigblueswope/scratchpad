import getpass
import json
import keyring
import os
import platform
import sys

# Max string length in a keychain
# https://stackoverflow.com/a/24165635/6178742
# 16,777,110 characters

# Max string length will apply to the keychain entry called 'orgs'
#  That is a python list of every org in the keychain and it 
#  is used to iterate over all orgs.

if platform.system() == 'Darwin':

    keychain_file = os.environ.get('API_AUTH_PATH')

    assert keychain_file, "OS Environment Variable 'API_AUTH_PATH' is not defined"

    kr = keyring.get_keyring()

    kr.keychain = str(keychain_file)



def get_orgs():
    '''
        Retrieves the list of orgs with api tokens in the Keychain
        
        The Keychain is defined in the OS Environment Variable KEYCHAIN_PATH
        
        Returns a sorted list with org names
    '''
    orgs = kr.get_password('orgs', '')
    
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

        assert org_name in get_orgs(), "%s is not in the list of orgs in the Keychain %s " % (org_name, keychain_file)

    token = kr.get_password(org_name, '')

    assert token, "{} does not have an entry in the Keychain {}".format(org_name, keychain_file)
    
    return token




def update_api_token(org_name, token_value=None):
    
    if not org_name:
        
        org_name = input('Org Name: ')
    
    if not token_value:
        
        token_value = input("API Token: ")

        assert token_value, "No token passed into function and no token value provided at prompt"


def set_api_token(org_name, token_value=None):

    if not org_name:

        org_name = input("Org Name: ")

    
    if not token_value:

        #token_value = getpass.getpass()
        token_value = input("API Token: ")
        assert token_value, "No token passed into function and no token value provided at prompt"
   

    # kr.set_password will update an existing item
    #   or create an item if it does not exist
    kr.set_password(org_name, '', token_value)

    existing_orgs = get_orgs()

    if not org_name in existing_orgs and not org_name == 'orgs':
        
        existing_orgs.append(org_name)
        
        updated_orgs = json.dumps(existing_orgs)
        
        kr.set_password('orgs', '', updated_orgs)
 



def delete_api_token(org_name=None):
    
    if not org_name:

        org_name = input("Org Name To Delete From The API Keyring: ")

    try:
        
        kr.delete_password(org_name, '')

    except keyring.errors.PasswordDeleteError:
        
        print(f'Could not delete api token for org: {org_name}')

    existing_orgs = get_orgs()

    if org_name in existing_orgs:
        
        existing_orgs.remove(org_name)

        updated_orgs = json.dumps(existing_orgs)
        
        kr.set_password('orgs', '', updated_orgs)

        print(f'Removed {org_name} from list of existing orgs')



def sync_orgs_with_tokens():

    existing_orgs = get_orgs()

    revised_orgs = []

    for org_name in existing_orgs:

        try:

            pw = get_api_token(org_name)

            revised_orgs.append(org_name)

        except AssertionError:

            print("No Token for {}".format(org_name))
    
    updated_orgs = json.dumps(revised_orgs)

    kr.set_password('orgs', '', updated_orgs)
    
 



def initialize_orgs():

    try:
        orgs = get_orgs()
    except TypeError:
        orgs = None

    if orgs:
        
        print("Keychain already contains an 'orgs' item. We will not overwrite the existing item.")

        sys.exit(1)

    else:

        set_api_token('orgs', '[]')




def iterate_keys():
    for item in keyring.get_keyring().get_preferred_collection().get_all_items():
        print(item.get_label(), item.get_attributes())
