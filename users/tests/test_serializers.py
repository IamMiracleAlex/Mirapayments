from rest_framework.test import APITestCase

from users.serializers import UserSerializer, UserUpdateSerializer


class UserSerializerTest(APITestCase):

    def test_user_serializer(self):
        '''Test user serializer'''

        data = {
            'email': 'miracle@mirapayments.com',
            'first_name': 'Miracle',
            'last_name': 'Alex',
            'phone': '08023456780',
            'country': 'Nigeria',
            'password': 'password',
            'account_name': 'Mirapayments'
        }
        user_serializer = UserSerializer(data=data)

        self.assertTrue(user_serializer.is_valid())


class UserUpdateSerializerTest(APITestCase):

    def test_user_update_serializer(self):
        '''Test user update serializer'''

        data = {
            'first_name': 'Miracle',
            'last_name': 'Alex',
            'phone': '08023456780',
            'country': 'Nigeria',
        }
        user_serializer = UserUpdateSerializer(data=data)

        self.assertTrue(user_serializer.is_valid())
   


