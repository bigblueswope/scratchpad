import argparse
import base64
import datetime
import json
import os
import requests
import sys
import time

import pyotp

import plat_auth


'''
# Body of suggested service being submitted
{"name":"PHP","tags":["HTTPHeaderSuggestor//PHP//5.6.32"],"id":"7073944c-766c-4db2-9be8-b1db9d27cb94","applicability":"2","creator_type":null,"creator_uuid":null,"criticality":"2","deleted":false,"description":"PHP is a server side scripting language and processor","enumerability":"4","first_time":"2018-10-03T14:46:34.161765+00:00","post_exploit":"3","private_weakness":"0","public_weakness":"3","randori_notes":"PHP 5.6.x has been discontinued and should not be used. This version of PHP has many known vulnerabilities of medium to high impact.","reference":null,"research":"4","svc_type":null,"sys_period":"[2018-12-12T00:50:57.873131+00:00,)","target_temptation":0,"time":"2018-10-03T14:46:34.161758+00:00","type":"global_service","vendor":"The PHP Group","version":"5.3.32","tt_factors":{"enumerability":"4","public_weakness":"3","private_weakness":"0","applicability":"2","research":"4","post_exploit":"3","criticality":"2"}}


#Body of existing service being submitted
{"name":"PHP","id":"7073944c-766c-4db2-9be8-b1db9d27cb94","applicability":2,"creator_type":null,"creator_uuid":null,"criticality":2,"deleted":false,"description":"PHP is a server side scripting language and processor","enumerability":4,"first_time":"2018-10-03T14:46:34.161765+00:00","post_exploit":3,"private_weakness":0,"public_weakness":3,"randori_notes":"PHP 5.6.x has been discontinued and should not be used. This version of PHP has many known vulnerabilities of medium to high impact.","reference":null,"research":4,"svc_type":null,"sys_period":"[2020-03-26T13:18:16.021252+00:00,)","target_temptation":0,"time":"2018-10-03T14:46:34.161758+00:00","type":"global_service","vendor":"The PHP Group","version":"5.6.32","tt_factors":{"enumerability":4,"public_weakness":3,"private_weakness":0,"applicability":2,"research":4,"post_exploit":3,"criticality":2}}
'''


class RandoriAuth(object):

    def __init__(self, u, p, h):
        self.sess = requests.Session()
        self.head = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US; q=0.7, en; q=0.3',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'user-agent': 'Mozilla'
            }
        self.username = u
        self.password = p
        self.host = h
        self.otp_seed = plat_auth.get_password(host, f'{username}-totp')
        self.org_id = ''
        self.randori_auth()


    def randori_auth(self,):
        """ Authentication Process """
        r1 = self.sess.get(f'https://{self.host}/', headers=self.head)
        
        auth_data = {'username': self.username, 'password': self.password}
        
        r2 = self.sess.post(f'https://{self.host}/auth/api/v1/login', headers=self.head, data=json.dumps(auth_data))
        
        totp = pyotp.TOTP(self.otp_seed)
        
        now = datetime.datetime.now()
        
        otp_token = totp.now()
        
        otp_body = {'otp': otp_token}
        
        r4 = self.sess.post(f'https://{self.host}/auth/api/v1/login-otp', headers=self.head, data=json.dumps(otp_body))
        
        r5 = self.sess.get(f'https://{self.host}/auth/api/v1/validate', headers=self.head)



if __name__ == '__main__':
    #host = 'ui.alpha.randori.io'
    host = 'alpha.randori.io'
    
    username = 'bj@randori.com'
    
    password = plat_auth.get_password(host, username)
    
    #request_url = 'https://{host}/ops/api/v1/add_or_update_service_and_clean_suggested_services'

    #url = f'https://{host}/aggregator/api/v1/services?limit=50&offset=0'

    f = RandoriAuth(username, password, host)
    
    #r6 = f.sess.get('https://ui.alpha.randori.io/#/dashboard/services', headers=f.head)
    #r6 = f.sess.get(url, headers=f.head)
    r6 = f.sess.get(f'https://{host}/recon/api/v1/hostname/792d837a-b132-4aed-b97f-97bed11d099d', headers=f.head)
    
    print(r6.json())
    #print(r6)
    
   
