from django.test import TestCase

from knox.tests.factories import AuthTokenFactory


class AuthTokenFactoryTest(TestCase):

    def test_model_creation(self):
        '''Assert that the AuthToken model was created with correct defaults'''

        auth_token = AuthTokenFactory()

        self.assertIsNotNone(auth_token.live_token) 
        self.assertIsNotNone(auth_token.user) 
        self.assertIsNotNone(auth_token.account) 
        self.assertIsNotNone(auth_token.created) 
        self.assertIsNotNone(auth_token.test_token) 
        self.assertEqual(auth_token.expiry, None) 