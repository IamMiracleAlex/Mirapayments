from django.db import models
from django.utils import timezone

from knox import crypto
from knox import defaults
from knox.defaults import CONSTANTS


class AuthTokenManager(models.Manager):
    def create(self, user, expiry=None):
        token = crypto.create_token_string()
        salt = crypto.create_salt_string()
        digest = crypto.hash_token(token, salt)
        test_token = crypto.create_test_token()

        if expiry is not None:
            expiry = timezone.now() + expiry

        instance = super(AuthTokenManager, self).create(
            token_key=token[:8], digest=digest,
            salt=salt, user=user, expiry=expiry, test_token=test_token)
        return instance, '{}{}'.format(defaults.LIVE_KEY_PREFIX, token)
    

class AuthToken(models.Model):

    objects = AuthTokenManager()

    digest = models.CharField(max_length=CONSTANTS.DIGEST_LENGTH, primary_key=True)
    token_key = models.CharField(max_length=CONSTANTS.TOKEN_KEY_LENGTH, db_index=True)
    salt = models.CharField(max_length=CONSTANTS.SALT_LENGTH, unique=True)
    user = models.ForeignKey('users.User', related_name='auth_token_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField(null=True, blank=True)
    test_token = models.CharField(max_length=64)

    def __str__(self):
        return '%s : %s' % (self.digest, self.user)
