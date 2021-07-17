from django.test import TestCase

from users.tests.factories import UserFactory


class UserTest(TestCase):

    def test_model_creation(self):
        '''Assert that the User model was created with correct defaults'''

        user = UserFactory()

        self.assertIsNotNone(user.first_name) 
        self.assertIsNotNone(user.phone) 
        self.assertIsNotNone(user.email) 
        self.assertFalse(user.is_superuser) 
        self.assertFalse(user.is_staff) 
        self.assertEqual(user.last_name, '') 

    # def test_queued(self):
    #     '''Assert that the queued property works'''
    
    #     user = UserFactory(status='green', known=False)

    #     self.assertTrue(user.queued)