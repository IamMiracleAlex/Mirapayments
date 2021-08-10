from django.contrib.auth import authenticate, login
from django.contrib.auth.signals import user_logged_in, user_logged_out

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework import status

from knox.models import AuthToken

from accounts.models import Account
from accounts.serializers import AccountSerializer
from users import serializers
from users.models import User
from users.signals import reset_password_token_created
from helpers.mailers import send_verification_email, send_password_reset_mail
from helpers.api_response import SuccessResponse, FailureResponse
from helpers.utils import validate_token

class LoginView(APIView):
    '''
    Login users
    POST: /users/login/
    '''
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        account_number = request.data.get("account_number")

        if email is None or password is None:
            return FailureResponse(
	            detail='Please provide both email and password',
				status=status.HTTP_400_BAD_REQUEST
			)
        user = authenticate(email=email, password=password)
        if not user:
            return FailureResponse(
				detail='Invalid credentials',
				status=status.HTTP_404_NOT_FOUND
            )
        if not user.email_verified:
            return FailureResponse(
                detail='Please verify your email address',
                status=status.HTTP_403_FORBIDDEN
            )
        login(request, user)

        user_logged_in.send(sender=request.user.__class__,
            request=request, user=request.user)    
        data = serializers.UserSerializer(user).data
       
        if user.accounts.all().count() > 1 and account_number:
            token = AuthToken.objects.filter(user=user, account__account_number=account_number).first()

        elif user.accounts.all().count() == 1:
            token = AuthToken.objects.filter(user=user).first()

        else:
            return SuccessResponse(detail="Choose account to login to", data=data, status=status.HTTP_300_MULTIPLE_CHOICES)

        data['live_token'] = token.live_token
        data['test_token'] = token.test_token
        return SuccessResponse(detail='Login successful', data=data)


class LogoutView(APIView):
    '''
    Log out users
    POST: /users/logout/
    '''
    def post(self, request, format=None):
        request._auth.delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        return SuccessResponse(None, status=status.HTTP_204_NO_CONTENT)

        
class LogoutAllView(APIView):
    '''
    Log the user out of all sessions
    I.E. deletes all auth tokens for the user
    POST: /users/logoutall/
    '''

    def post(self, request):
        request.user.auth_token_set.all().delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        return SuccessResponse(None, status=status.HTTP_204_NO_CONTENT)

class SignUpView(APIView):
    '''
    Create new user accounts
    POST: /users/signup/
    '''
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
                 
            send_verification_email(user)
            return SuccessResponse(
                detail='User created successfully',
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
				

class UserDetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve users and update user details
    GET: /users/me/
    PUT: /users/me/
    """
    # queryset = User.objects.all()
    # serializer_class = serializers.UserSerializer
    
    def get(self, request, *args, **kwargs):
        data = serializers.UserSerializer(instance=request.user).data
        return SuccessResponse(data=data)
    
    def put(self, request, *args, **kwargs):
        serializer = serializers.UserUpdateSerializer()
        updated_user = serializer.update(request.user, request.data)
        return SuccessResponse(
            detail='User updated successfully',
            data=serializers.UserSerializer(updated_user).data,
        )


class SendVerificationEmail(APIView):
    '''
    Send verification email
    POST: /users/send-verification-email/
    '''
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return FailureResponse(detail='Please provide an email')

        user = User.objects.filter(email=email)
        if user.exists(): 
            send_verification_email(user.first())
            return SuccessResponse(detail='Email sent successfully')


class VerifyEmail(APIView):
    '''
    Verify the email
    POST: /users/verify-email/uidb64/token/
    '''
    permission_classes = [AllowAny]
    
    def get(self, request, uidb64, token, *args, **kwargs):

        user, is_valid = validate_token(uidb64, token)
  
        if user and is_valid:

            if user.email_verified:
                return SuccessResponse(detail='Your email has already been verified')
            
            user.email_verified = True
            user.save()
            return SuccessResponse(detail='Email verification was successful')

        else:
            return FailureResponse(detail='Email verification failed. Token is either invalid or expired')


class ResetPasswordRequest(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        An api view which provides a method to request a password reset token based on an e-mail address
        Sends a signal reset_password_token_created when a reset token was created.
        POST: /users/password-reset-request/
        """

        email = request.data.get('email')
        if not email:
            return FailureResponse(detail='Email is required')

        # find a user by email address (case insensitive search)
        user = User.objects.filter(email__iexact=email)

        if user.exists() and getattr(user.first(), 'is_active', False):
            send_password_reset_mail(user.first())            
            # send a signal that the password token was created
            reset_password_token_created.send(sender=self.__class__, user=self)
            return SuccessResponse(detail='Kindly check your email to set your password')


class ResetPasswordValidateToken(APIView):
    """
    An api view which provides a method to verify that a token is valid
    POST: /users/reset-password-validate-token/
    """
    permission_classes = [AllowAny]
    serializer_class = serializers.ValidateTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return SuccessResponse(detail="Token is valid")



class ResetPasswordConfirm(APIView):
    """
    An Api View which provides a method to reset a password based on a unique token
    POST: /users/reset-password-confirm/
    """
    permission_classes = [AllowAny]
    serializer_class = serializers.ResetPasswordConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.reset_password()
        return SuccessResponse(detail="Password reset was successful")

    
class UserInvitationView(APIView):
    '''
    Invite account user
    POST: /users/invite/
    '''

    def post(self, request):
        #TODO: check if a user is permitted to invite
        serializer = serializers.UserInvitationSerializer(data=request.data, user=request.user)
        if serializer.is_valid(raise_exception=True):
            serializer.invite()

        return SuccessResponse(detail='Invite has been sent to new user')


class ListAccountUsersView(APIView):
    '''
    List all users tied to an account
    GET: /users/list/<account_number>/
    '''
    def get(self, request, account_number):
        account = Account.objects.get(account_number=account_number)
        users = account.user_set.all()
        data = serializers.UserSerializer(instance=users, many=True).data
        return SuccessResponse(data=data)


class ListUserAccountsView(APIView):
    ''''
    List all accounts tied to a user
    GET: /users/me/accounts/
    '''
    def get(self, request):
        accounts = request.user.accounts.all()
        data = AccountSerializer(instance=accounts, many=True).data
        return SuccessResponse(data=data)


class ActivateInvitedUser(APIView):
    '''
    Add an invited user
    POST: /users/activate/
    '''
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.ActivateInvitedUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.activate()
        
        return SuccessResponse(detail='User successfully activated')



