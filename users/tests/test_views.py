from rest_framework import status
from rest_framework.test import APITestCase

from users.tests.factories import UserFactory
from knox.models import AuthToken

class LoginViewTest(APITestCase):   

    @classmethod
    def setUpTestData(cls):
        cls.auth_data = { 
            'phone': '2348026043569',
            'password': '@password123',
            'email': 'miracle@mirapayments.com'
        }     
        cls.url = '/users/login/'
        cls.user = UserFactory(**cls.auth_data)

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
        self.assertEqual(resp.data['detail'], 'Please provide both phone number and password')

    def test_unverified_email(self):
        '''Assert user can't login with unverified email'''

        login = self.client.post(self.url, data=self.auth_data)
        self.assertEqual(login.status_code, 403)
        self.assertEqual(login.data['detail'], 'Please verify your email address')

    def test_login(self):
        '''Login with correct credentials'''

        # verify email
        self.user.email_verified = True  #sure this hits db?
        self.user.save()

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
                    'country': 'Nigeria',
                    }

    def test_user_creation(self):
        '''Test create new user '''

        resp = self.client.post(self.url, self.data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('User created', resp.data['detail'])

    def test_token_and_json_data_are_returned(self):
        '''Test that token and json data are returned'''

        resp = self.client.post(self.url, self.data)
        expected = r'^\w+$'  #token format

        self.assertRegex(resp.data['data']['live_token'], expected)
        self.assertRegex(resp.data['data']['test_token'], expected)
        self.assertEqual(resp.data['data']['email'], self.data['email'])



class UserDetailUpdateViewTest(APITestCase):

    def setUp(self):

        self.detail_url = '/users/me/'
        self.user = UserFactory()

        #  # get token
        # self.token = AuthToken.objects.create(user=self.user)

    def test_user_details_get_method(self):
        '''Assert that get method for user details works. user is retrieved by their token'''
         
        # # authorize token
        # self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.live_token}')        
        # resp = self.client.get(self.detail_url)

        self.client.force_login(self.user)
        resp = self.client.get(self.detail_url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['data']['phone'], self.user.phone)

    def test_user_detail_put_method(self):
        '''Assert that put method for user details works. Data is sent to the user using their token'''

        # # authorize token
        # self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.live_token}')       
        #  
        new_data = {'first_name':'Miracle', 
                    'last_name':'Alex',
                    'email': 'example@gmail.com'} 

        # update data and assert they were updated
        self.client.force_login(self.user)
        resp = self.client.put(self.detail_url, new_data) 

        self.assertEqual(resp.data['data']['phone'], self.user.phone)
        self.assertEqual(resp.data['data']['first_name'], new_data['first_name'])
        self.assertEqual(resp.data['data']['last_name'], new_data['last_name'])
