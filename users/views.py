from django.contrib.auth import authenticate
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth.tokens import default_token_generator  
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework import status

from knox.models import AuthToken

from users.serializers import UserSerializer, UserUpdateSerializer
from users.models import User
from users.utils import send_activation_email
from helpers.api_response import SuccessResponse, FailureResponse


class LoginView(APIView):
    '''
    Login users
    POST: /users/logim/
    '''
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
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
        user_logged_in.send(sender=request.user.__class__,
            request=request, user=request.user)    
        data = UserSerializer(user).data
        instances = AuthToken.objects.filter(user=user)
        token = instances.first()
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

class SignUpView(APIView):
    '''
    Create new user accounts
    POST: /users/signup/
    '''
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            instance = AuthToken.objects.create(user=user)
            data = serializer.data
            # do we really need to send the token on signup?
            # data['live_token'] = instance.live_token
            # data['test_token'] = instance.test_token
            send_activation_email(request, user)
            return SuccessResponse(
                detail='User created successfully',
                data=data,
                status=status.HTTP_201_CREATED
            )
				

class UserDetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve users and update user details
    GET: /users/me/
    PUT: /users/me/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get(self, request, *args, **kwargs):
        data = UserSerializer(instance=request.user).data
        return SuccessResponse(data=data)
    
    def put(self, request, *args, **kwargs):
        serializer = UserUpdateSerializer()
        updated_user = serializer.update(request.user, request.data)
        return SuccessResponse(
            detail='User updated successfully',
            data=UserSerializer(updated_user).data,
        )


class SendVerificationEmail(APIView):
    '''
    Send verification email
    POST: /users/send-verification-email/
    '''
    def post(self, request):
        send_activation_email(request, request.user)
        return SuccessResponse(detail='Email sent Successfully')


class VerifyEmail(APIView):
    '''
    Verify the email
    POST: /users/verify-email/uidb64/token/
    '''
    permission_classes = [AllowAny]
    
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        # print(id)    
        # print(user)
        # print(token)
        # print(uidb64)
        # print(default_token_generator.check_token(user, token))
        if user and default_token_generator.check_token(user, token):

            if user.email_verified:
                return SuccessResponse(detail='Your email has already been verified')
            
            user.email_verified = True
            user.save()
            return SuccessResponse(detail='Email verification was successful')

        else:
            return FailureResponse(detail='Email verification failed')


		


# def test_email(request):
# 	account_activation_token = AccountActivationTokenGenerator()
# 	user = CustomUser.objects.first()
# 	context = {
# 		'name': user.first_name,
# 		'email': user.email,
# 		'domain': get_current_site(request).domain,
# 		'uid': urlsafe_base64_encode(force_bytes(user.id)),
# 		'token': account_activation_token.make_token(user),
# 	}
# 	# return render(request, 'emails/activate_email.html', context=context)
# 	# return render(request, 'emails/transaction_failed.html', context=context)
# 	return render(request, 'emails/safelock_maturity.html', context=context)
# 	# return render(request, 'emails/transaction_success.html', context=context)


# @shared_task
# def generate_account_number(user_id):
# 	user = CustomUser.objects.get(id=user_id)
# 	monnify = MonnifyService()
# 	res = monnify.create_reserved_accounts(user)
# 	if (res['requestSuccessful'] == True):
# 		user.account_number = res['responseBody']['accountNumber']
# 		user.account_bank_name = res['responseBody']['bankName']
# 		user.save()
# 		return user



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    





