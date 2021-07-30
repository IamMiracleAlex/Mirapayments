import binascii
from os import urandom

from django.db import models
from django.utils import timezone

from knox import defaults


class AuthTokenManager(models.Manager):
    def create(self, user, account, expiry=None):

        def create_live_token():
            live_token = binascii.hexlify(urandom(20)).decode()
            return '{}{}'.format(defaults.LIVE_KEY_PREFIX, live_token)

        def create_test_token():
            test_token = binascii.hexlify(urandom(20)).decode()
            return '{}{}'.format(defaults.TEST_KEY_PREFIX, test_token)

        if expiry is not None:
            expiry = timezone.now() + expiry

        instance = super(AuthTokenManager, self).create(
            live_token=create_live_token(), test_token=create_test_token(),
            user=user, account=account, expiry=expiry)
        return instance
    

class AuthToken(models.Model):

    objects = AuthTokenManager()

    live_token = models.CharField(max_length=64, db_index=True)
    user = models.ForeignKey('users.User', related_name='auth_token_set', on_delete=models.CASCADE)
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField(null=True, blank=True)
    test_token = models.CharField(max_length=64)

    def __str__(self):
        return '%s : %s' % (self.test_token, self.user)
