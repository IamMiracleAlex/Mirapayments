try:
    from hmac import compare_digest
except ImportError:
    def compare_digest(a, b):
        return a == b

from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header,
)

from knox.models import AuthToken
from knox import defaults


class TokenAuthentication(BaseAuthentication):
    #######
    ######
    # PROTECTED CLASS: DO NOT MODIFY!!!
    ######
    #######

    '''
    This authentication scheme uses Knox AuthTokens for authentication.

    Similar to DRF's TokenAuthentication, it overrides a large amount of that
    authentication scheme, have live and test tokens

    If successful
    - `request.user` will be a django `User` instance
    - `request.auth` will be an `AuthToken` instance
    '''
    model = AuthToken

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
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
            for auth_token in AuthToken.objects.filter(live_token=token):
               
                if compare_digest(token, auth_token.live_token):
                    return self.validate_user(auth_token, is_live=True)

        elif token.startswith(defaults.TEST_KEY_PREFIX):
            for auth_token in AuthToken.objects.filter(test_token=token):
        
                if compare_digest(token, auth_token.test_token):
                    return self.validate_user(auth_token, is_live=False)        

        raise exceptions.AuthenticationFailed(msg)


    def validate_user(self, auth_token, is_live):
        if not auth_token.user.is_active:
            raise exceptions.AuthenticationFailed(
                _('User inactive or deleted.'))
        return (auth_token.user, auth_token, is_live)

    def authenticate_header(self, request):
        return defaults.AUTH_HEADER_PREFIX

