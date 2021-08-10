from django.core import mail
from django.test.utils import override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

from rest_framework.test import APITestCase

from users.serializers import ( ActivateInvitedUserSerializer, UserInvitationSerializer, 
UserSerializer, UserUpdateSerializer, ResetPasswordConfirmSerializer, ValidateTokenSerializer )
from users.tests.factories import UserFactory
from accounts.tests.factories import AccountFactory


class UserSerializerTest(APITestCase):

    def test_user_serializer(self):
        '''Test user serializer :is_valid() and :create() methods'''

        # create incomplete data
        data = {
            'email': 'miracle@mirapayments.com',
            'first_name': 'Miracle',
            'last_name': 'Alex',
            'phone': '08023456780',
            'password': 'password',
        }
        invalid_serializer = UserSerializer(data=data)

        # assert serilizer data checks validity
        self.assertFalse(invalid_serializer.is_valid())

        # complete data
        data['account_name'] = 'Mirapayments'
        valid_serializer = UserSerializer(data=data)

        self.assertTrue(valid_serializer.is_valid())

        # assert a user is returned when :create() method is called
        user = valid_serializer.create(valid_serializer.validated_data)
        self.assertEqual(user.email, data['email'])


class UserUpdateSerializerTest(APITestCase):

    def test_user_update_serializer(self):
        '''Test user update serializer :isvalid() and :update() methods'''

        data = {
            'first_name': 'Miracle',
            'last_name': 'Alex',
            'phone': '08023456780',
            'country': 'Nigeria',
        }
        user_serializer = UserUpdateSerializer(data=data)

        # assert serilizers checks validity correctly
        self.assertTrue(user_serializer.is_valid())

        # assert :update() method works as expected
        old_user = UserFactory()
        self.assertNotEqual(old_user.first_name, data['first_name'])

        updated_user = user_serializer.update(old_user, user_serializer.validated_data)
        self.assertEqual(updated_user.first_name, data['first_name'])
   

class UserInvitationSerializerTest(APITestCase):

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_user_invitation(self):
        '''Test user invitation serializer :is_valid() and :invite() methods'''

        inviter = UserFactory()
        data = {
            'email': 'new_user@mirapayments.com',
            'role': 'operations',
        }
        # check validity
        invalid_invite_serializer = UserInvitationSerializer(data=data, user=inviter)
        self.assertFalse(invalid_invite_serializer.is_valid())
       
       # update data
        account = AccountFactory()
        data['account_number'] = account.account_number
        valid_invite_serializer = UserInvitationSerializer(data=data, user=inviter)

        self.assertTrue(valid_invite_serializer.is_valid())

        valid_invite_serializer.invite() # invite user

        # assert invite mail was sent
        self.assertEqual(len(mail.outbox), 1)
        

class ActivateInvitedUserSerializerTest(APITestCase):
    def test_invited_user_activation(self):
        '''Test the invited user activation serializer :is_active() and :activate() methods'''
  
        # check validity with incomplete payload
        data = {
            'password': '@qwfmnjfkemd123'
        }
        invalid_activate_serializer = ActivateInvitedUserSerializer(data=data)
        self.assertFalse(invalid_activate_serializer.is_valid())

        # update payload and check validity again
        invited_user =  UserFactory(is_active=False)
        uid =  urlsafe_base64_encode(force_bytes(invited_user.id))
        data['uid'] = uid
        valid_activate_serializer = ActivateInvitedUserSerializer(data=data)
        self.assertTrue(valid_activate_serializer.is_valid())

        # activate user and assert they are activated
        activated_user = valid_activate_serializer.activate()
        self.assertTrue(activated_user.is_active)


class ResetPasswordSerializerTest(APITestCase):
    
    def test_token_validation(self):
        '''Assert that token validation works as expected for the reset password 
        serializers - :is_valid() and :validate_token() methods
        '''

        # create data
        user = UserFactory()
        token = default_token_generator.make_token(user)
        uid =  urlsafe_base64_encode(force_bytes(user.id))
        data = {
            'uid': uid,
            'token': token,
        }
        # check validity of both serializers
        invalid_rpc_serializer = ResetPasswordConfirmSerializer(data=data)
        valid_vt_serializer = ValidateTokenSerializer(data=data)
        self.assertFalse(invalid_rpc_serializer.is_valid())
        self.assertTrue(valid_vt_serializer.is_valid())

        # update data for invalid serializer 
        data['password'] = '@thiscool123'

        # Assert serializer is now valid and reset password
        valid_rpc_serializer = ResetPasswordConfirmSerializer(data=data)
        self.assertTrue(valid_rpc_serializer.is_valid())
        valid_rpc_serializer.reset_password()

        # Assert password has been changed
        self.assertNotEqual(valid_rpc_serializer.user.password, user.password)





