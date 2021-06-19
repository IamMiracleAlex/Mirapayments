# Use this module to test functions & run arbitrary scripts
#within the context of this application.
# The block below must not be removed and must come firsr before any imports.
print("Initializing script runner...", end="")
######################################################################
import os                                                            #
import django                                                        #
                                                                     #
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mirapayments.settings")   #
django.setup()                                                       #
######################################################################
print("Ready!")




# def process():
#     # write your code here
#     pass


# process()
import time

from knox.crypto import hash_token as knox_hash_token
from knox.crypto import create_token_string, create_salt_string
from knox.crypto import create_test_token

d1 = time.time()
token_string = create_token_string()
d2 = time.time()

salt = create_salt_string()

k1 = time.time()
knox_hash = knox_hash_token(token_string, salt)
k2 = time.time()



p1 = time.time()
test = create_test_token()
p2 = time.time()

print('knox', knox_hash, k2-k1)
print('token_string', token_string, d2-d1)
print('test', test, p2-p1)