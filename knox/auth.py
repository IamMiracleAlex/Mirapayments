try:
    from hmac import compare_digest
except ImportError:
    def compare_digest(a, b):
        return a == b

import binascii

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header,
)

from knox.crypto import hash_token
from knox.models import AuthToken
from knox.signals import token_expired
from knox import defaults
from knox.defaults import CONSTANTS

from users.models import User

class TokenAuthentication(BaseAuthentication):
    #######
    ######
    # PROTECTED CLASS: DO NOT MODIFY!!!
    ######
    #######

    '''
    This authentication scheme uses Knox AuthTokens for authentication.

    Similar to DRF's TokenAuthentication, it overrides a large amount of that
    authentication scheme to cope with the fact that Tokens are not stored
    in plaintext in the database

    If successful
    - `request.user` will be a django `User` instance
    - `request.auth` will be an `AuthToken` instance
    '''
    model = AuthToken

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        # prefix = defaults.AUTH_HEADER_PREFIX.encode()
        prefix = defaults.AUTH_HEADER_PREFIX.encode()

        if not auth or auth[0].lower() != prefix.lower():
            return None
        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. '
                    'Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)
        
        user, auth_token, is_live = self.authenticate_credentials(auth[1])
        setattr(request, 'is_live', is_live)
        return (user, auth_token)

    def authenticate_credentials(self, token):
        '''
        Due to the random nature of hashing a salted value, this must inspect
        each auth_token individually to find the correct one.

        Tokens that have expired will be deleted and skipped
        '''
        msg = _('Invalid token.')
        token = token.decode("utf-8")

        if token.startswith(defaults.LIVE_KEY_PREFIX):
            token = token.lstrip(defaults.LIVE_KEY_PREFIX)
            for auth_token in AuthToken.objects.filter(live_token=token):
                # if self._cleanup_token(auth_token):
                #                     continue
                if compare_digest(token, auth_token.live_token):
                    if defaults.AUTO_REFRESH and auth_token.expiry:
                        self.renew_token(auth_token)
                    return self.validate_user(auth_token, is_live=True)

        elif token.startswith(defaults.TEST_KEY_PREFIX):
            for auth_token in AuthToken.objects.filter(test_token=token):
                # if self._cleanup_token(auth_token):
                #     continue

                if compare_digest(token, auth_token.test_token):
                    return self.validate_user(auth_token, is_live=False)        

        raise exceptions.AuthenticationFailed(msg)

    def renew_token(self, auth_token):
        current_expiry = auth_token.expiry
        new_expiry = timezone.now() + defaults.TOKEN_TTL
        auth_token.expiry = new_expiry
        # Throttle refreshing of token to avoid db writes
        delta = (new_expiry - current_expiry).total_seconds()
        if delta > defaults.MIN_REFRESH_INTERVAL:
            auth_token.save(update_fields=('expiry',))

    def validate_user(self, auth_token, is_live):
        if not auth_token.user.is_active:
            raise exceptions.AuthenticationFailed(
                _('User inactive or deleted.'))
        return (auth_token.user, auth_token, is_live)

    def authenticate_header(self, request):
        return defaults.AUTH_HEADER_PREFIX

    def _cleanup_token(self, auth_token):
        for other_token in auth_token.user.auth_token_set.all():
            if other_token.digest != auth_token.digest and other_token.expiry:
                if other_token.expiry < timezone.now():
                    other_token.delete()
                    username = other_token.user.get_username()
                    token_expired.send(sender=self.__class__,
                                       username=username, source="other_token")
        if auth_token.expiry is not None:
            if auth_token.expiry < timezone.now():
                username = auth_token.user.get_username()
                auth_token.delete()
                token_expired.send(sender=self.__class__,
                                   username=username, source="auth_token")
                return True
        return False
