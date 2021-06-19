import binascii
from os import urandom as generate_bytes

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.hashes import SHA512

from knox import defaults

sha = SHA512


def create_token_string():
    return binascii.hexlify(generate_bytes(32)).decode()


def create_salt_string():
    return binascii.hexlify(generate_bytes(8)).decode()


def hash_token(token, salt):
    '''
    Calculates the hash of a token and salt.
    input is unhexlified

    token and salt must contain an even number of hex digits or
    a binascii.Error exception will be raised
    '''
    digest = hashes.Hash(sha(), backend=default_backend())
    digest.update(binascii.unhexlify(token))
    digest.update(binascii.unhexlify(salt))
    return binascii.hexlify(digest.finalize()).decode()


def create_test_token():
    key = binascii.hexlify(generate_bytes(20)).decode()
    return '{}{}'.format(defaults.TEST_KEY_PREFIX, key)
