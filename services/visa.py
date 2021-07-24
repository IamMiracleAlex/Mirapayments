import os
import datetime
import logging
import http.client as http_client

import requests
from dotenv import load_dotenv

http_client.HTTPSConnection.debuglevel = 0
load_dotenv()

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


class Visa:
    user_id = os.environ.get('VISA_USERID')
    password = os.environ.get('VISA_PASSWORD')
    cert = 'services/certificates/visa_cert.pem'
    key = 'services/certificates/visa_private_key.pem'
    timeout = 30
    
    @classmethod
    def request(cls, method: str, url: str, headers: dict = {}, data: dict = {},  timeout: int = timeout):
        '''Send requests to Visa using Two-Way (Mutual) SSL'''

        headers = headers.update({
            'X-Transaction-Timeout-MS': timeout
        })
        response = requests.request(
                                method,
                                url,
                                cert=(cls.cert, cls.key),
                                headers = headers,
                                auth=(cls.user_id, cls.password),
                                data = data,
                                timeout=timeout
                                )

        return response

    @classmethod
    def hello_world(cls):
        '''Mutual auth hello world request'''

        response = cls.request(
                        method='get', 
                        url='https://sandbox.api.visa.com/vdp/helloworld'
                        )
        return response

    @classmethod
    def pull_funds(cls):
        '''
        pull funds from the sender's Visa account
        https://developer.visa.com/capabilities/visa_direct/reference#visa_direct__funds_transfer__v1__pullfunds
        '''
        pass

print(Visa.hello_world().json())