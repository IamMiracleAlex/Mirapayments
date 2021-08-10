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
      
    def test_send_verification_email_url_resolves_to_view(self):
        '''assert that the send verification url resolves to the accurate view'''

        found = resolve('/users/send-verification-email/')
        self.assertEquals(found.func.view_class, views.SendVerificationEmail)         
      
    def test_verify_email_url_resolves_to_view(self):
        '''assert that the verify email url resolves to  correct view'''

        found = resolve('/users/verify-email/uidb64/token/')
        self.assertEquals(found.func.view_class, views.VerifyEmail)         
      
    def test_password_reset_request_url_resolves_to_view(self):
        '''assert that the password reset request url resolves to the right view'''

        found = resolve('/users/password-reset-request/')
        self.assertEquals(found.func.view_class, views.ResetPasswordRequest)         
      
    def test_reset_password_validate_token_url_resolves_to_view(self):
        '''assert that the reset password validate token url resolves to the correct view'''

        found = resolve('/users/reset-password-validate-token/')
        self.assertEquals(found.func.view_class, views.ResetPasswordValidateToken)         
      
      
    def test_reset_password_confirm_url_resolves_to_view(self):
        '''assert that the reset password confirm url resolves to the correct view'''

        found = resolve('/users/reset-password-confirm/')
        self.assertEquals(found.func.view_class, views.ResetPasswordConfirm)         
      
      
    def test_user_invite_url_resolves_to_view(self):
        '''assert that the user invite url resolves to the correct view'''

        found = resolve('/users/invite/')
        self.assertEquals(found.func.view_class, views.UserInvitationView)         
      
      
    def test_list_account_users_url_resolves_to_view(self):
        '''assert that the list account users url resolves to the correct view'''

        found = resolve('/users/list/123456/')
        self.assertEquals(found.func.view_class, views.ListAccountUsersView)         
      
      
    def test_list_user_accounts_url_resolves_to_view(self):
        '''assert that the list user accounts url resolves to the correct view'''

        found = resolve('/users/me/accounts/')
        self.assertEquals(found.func.view_class, views.ListUserAccountsView)         
      
      
    def test_activate_invited_user_url_resolves_to_detail_view(self):
        '''assert that the activate invited user url resolves to the correct view'''

        found = resolve('/users/activate/')
        self.assertEquals(found.func.view_class, views.ActivateInvitedUser)         
      
