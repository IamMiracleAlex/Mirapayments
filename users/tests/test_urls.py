from django.test import SimpleTestCase
from django.urls import resolve

from users import views


class UserUrlsResolvesToViewTest(SimpleTestCase):

    def test_login_url_resolves_to_login_view(self):
        '''assert that login url resolves to the login view class'''

        found = resolve('/users/login/')
        # use func.view_class to get the class for the view
        self.assertEquals(found.func.view_class, views.LoginView)

    
    def test_logout_url_resolves_to_logout_view(self):
        '''assert that the logout url resolves to the logout view class'''

        found = resolve('/users/logout/')
        self.assertEquals(found.func.view_class, views.LogoutView) 

    
    def test_signup_url_resolves_to_register_view(self):
        '''assert that the signup url resolves to the register view'''

        found = resolve('/users/signup/')
        self.assertEquals(found.func.view_class, views.SignUpView)       
      
    
    def test_user_detail_update_url_resolves_to_detail_view(self):
        '''assert that the user me url resolves to the user detail & update view'''

        found = resolve('/users/me/')
        self.assertEquals(found.func.view_class, views.UserDetailUpdateView)         
      
