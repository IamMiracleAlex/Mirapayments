from rest_framework.settings import api_settings

TEST_KEY_PREFIX = 'test_sk_'
LIVE_KEY_PREFIX = 'live_sk_'
TOKEN_TTL = None
USER_SERIALIZER = 'knox.serializers.UserSerializer'
TOKEN_LIMIT_PER_USER = 4
AUTO_REFRESH = False
MIN_REFRESH_INTERVAL = 60
AUTH_HEADER_PREFIX = 'Token'
EXPIRY_DATETIME_FORMAT = api_settings.DATETIME_FORMAT
