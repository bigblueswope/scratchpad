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


'''
keyring examples:

create new keyring item:
keyring.set_password('site_name', 'username', 'password')

retrieve password:
keyring.get_password('site_name', 'username')

'''


if platform.system() == 'Darwin':

    keychain_file = os.environ.get('PLAT_AUTH_PATH')

    assert keychain_file, "OS Environment Variable 'PLAT_AUTH_PATH' is not defined"

    kr = keyring.get_keyring()
    
    kr.keychain = str(keychain_file)


def get_password(site, username):

    if not site:
        site = input("Site: ")

    if not username:
        username = input("Username: ")

    password = kr.get_password(site, username)
    
    return password 



def get_totp_seed(site, username):

    if not site:
        site = input("Site: ")

    if not username:
        username = input("Username: ")
    
    if not username.endswith('-totp'):
        totp_username = username + '-totp'

    seed = kr.get_password(site, totp_username)
    
    return seed 


