from unittest import skip

from django.core import mail
from django.test.utils import override_settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from users.tests.factories import UserFactory
from knox.tests.factories import AuthTokenFactory
from accounts.tests.factories import AccountFactory


class LoginViewTest(APITestCase):   

    @classmethod
    def setUpTestData(cls):
        cls.auth_data = { 
            'password': '@password123',
            'email': 'miracle@mirapayments.com'
        }     
        cls.url = '/users/login/'

    def test_invalid_user(self):
        '''login with invalid credentials'''

        data = { 
            'email': 'email@gmail.com',
            'password': 'password1000'
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.data['detail'], 'Invalid credentials')

    def test_incomplete_credentials(self):
        '''Login with incomplete credentials'''

        data = { 
            'email': 'miracle@mirapayments.com'
        }
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data['detail'], 'Please provide both email and password')

    def test_unverified_email(self):
        '''Assert user can't login with unverified email'''
        UserFactory(**self.auth_data)

        login = self.client.post(self.url, data=self.auth_data)
        self.assertEqual(login.status_code, 403)
        self.assertEqual(login.data['detail'], 'Please verify your email address')
       
    def test_login(self):
        '''Login with correct credentials'''

        # set up data
        user = UserFactory(**self.auth_data, email_verified=True)
        account = AccountFactory()
        user.accounts.add(account)
        AuthTokenFactory(user=user, account=account)
       
        login = self.client.post(self.url, data=self.auth_data)
       
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.data['detail'], 'Login successful')
        self.client.logout()


class SignUpViewTest(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.url = '/users/signup/'
        cls.data = {'phone':'08026043569', 
                    'password':'password123',
                    'email':'email@example.com',
                    'first_name': 'Miracle',
                    'last_name': 'Alex',
                    'account_name': 'Mirapayments'
                    }

    def test_user_creation(self):
        '''Test create new user '''

        resp = self.client.post(self.url, self.data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('User created', resp.data['detail'])
        self.assertEqual(resp.data['data']['email'], self.data['email'])


class UserDetailUpdateViewTest(APITestCase):

    def setUp(self):

        self.detail_url = '/users/me/'
        self.user = UserFactory()

    def test_user_details_get_method(self):
        '''Assert that get method for user details works. user is retrieved by their token'''
         
        self.client.force_authenticate(self.user)       
        resp = self.client.get(self.detail_url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['data']['phone'], self.user.phone)

    def test_user_detail_put_method(self):
        '''Assert that put method for user details works. Data is sent to the user using their token'''

        new_data = {'first_name':'Miracle', 
                    'last_name':'Alex',
                    'email': 'example@gmail.com'} 

        # update data and assert they were updated
        self.client.force_authenticate(self.user)       
        resp = self.client.put(self.detail_url, new_data) 

        self.assertEqual(resp.data['data']['phone'], self.user.phone)
        self.assertEqual(resp.data['data']['first_name'], new_data['first_name'])
        self.assertEqual(resp.data['data']['last_name'], new_data['last_name'])


class VerificationEmailTest(APITestCase):

    def setUp(self):
        self.signup_url = '/users/signup/'
        self.data = {'phone':'08026043569', 
                    'password':'password123',
                    'email':'email@example.com',
                    'first_name': 'Miracle',
                    'last_name': 'Alex',
                    'account_name': 'Mirapayments'
                }

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_verification_email(self):
        '''Assert that verification email is sent'''

        # sign up a new user
        resp = self.client.post(self.signup_url, data=self.data)
        # assert that verification mail was sent on signup
        self.assertEqual(len(mail.outbox), 1)
      
        # try to resend verification email
        invite_url = '/users/send-verification-email/'
        email = resp.data['data']['email']
        
        resp = self.client.post(invite_url, {'email': email})

        # assert request is successfull and mail was sent
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 2)

    def test_token_verification(self):
        '''Assert that tokens verification works as expected'''

        # create a user and tokens
        user = UserFactory()
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = default_token_generator.make_token(user)

        verify_url = f'/users/verify-email/{uidb64}/{token}/'
        resp = self.client.get(verify_url)

        # Assert email was verified
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['detail'], 'Email verification was successful')

        # Assert email already verified
        resp = self.client.get(verify_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['detail'], 'Your email has already been verified')

        # Assert email verification failure with invalid token
        new_token = 'this-is-an-invalid-token'
        verify_url = f'/users/verify-email/{uidb64}/{new_token}/'
        resp = self.client.get(verify_url)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email verification failed', resp.data['detail'])


class PasswordResetTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_request(self):
        '''Assert that password reset token was sent'''

        pwd_req_url = '/users/password-reset-request/'
        resp = self.client.post(pwd_req_url, {'email': self.user.email})

        # assert request is successfull and mail was sent
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_validate_token(self):
        '''Assert that token is valid'''

        # create a user and tokens
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))
        token = default_token_generator.make_token(self.user)

        # test validate token url
        validate_token_url = '/users/reset-password-validate-token/'
        validate_token_data = {'uid': uidb64, 'token': token}
        resp = self.client.post(validate_token_url, validate_token_data)

        # Assert validate token is  successful
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['detail'], 'Token is valid')

    def test_password_reset_confirm(self):
        '''Assert that reset was confirmed'''

        # create a user and tokens
        user = UserFactory(email="email@gmail.com")
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = default_token_generator.make_token(user)

        # Assert password is reset
        pwd_reset_confirm_url = '/users/reset-password-confirm/'
        pwd_reset_confirm_data = {
            'uid': uidb64, 'token': token, 'password': 'mirapayments'
        }
        resp = self.client.post(pwd_reset_confirm_url, pwd_reset_confirm_data)
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['detail'], 'Password reset was successful')
