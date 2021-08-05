from django.contrib.auth import authenticate, login
from django.contrib.auth.signals import user_logged_in, user_logged_out

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework import status

from knox.models import AuthToken

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
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    
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
    def post(self, request):
        send_verification_email(request.user)
        return SuccessResponse(detail='Email sent Successfully')


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

    def post(self, request):
        '''
        Invite account user
        POST: /users/invite/
        '''

        serializer = serializers.UserInvitationSerializer(request.data)
        if serializer.is_valid():
            serializer.invite()

        # staff_form = CompanyStaffRegistration(request.user, request.POST)
        # if request.user.user_type.user_type == 'Admin':
        #     if staff_form.is_valid():
        #         my_staff = staff_form.save(commit=False)
        #         my_staff.company = request.user.company
        #         my_staff.is_active = False
        #         my_staff.save()

        #         user_id = urlsafe_base64_encode(force_bytes(my_staff.pk))
        #         token = user_tokenizer.make_token(my_staff)
        #         employee_company = my_staff.company
        #         employee_email = my_staff.email
        #         company_slug = my_staff.company.company_slug
        #         message = 'http://' + settings.MY_SERVER + reverse('account:staff_set_password',
        #                                                            kwargs={'company_slug': company_slug,
        #                                                                    'user_id': user_id, 'token': token})
        #         new_employee_created.send(
        #             sender=my_staff,
        #             company=employee_company,
        #             message=message,
        #             email=employee_email,
        #             company_slug=company_slug,
        #             notification_type="NEW_STAFF_CREATED"
        #         )
        #         messages.add_message(request, messages.SUCCESS, "Company Employee added Successfully")
        #         return redirect('account:profile', request.user.email, request.user.company.company_slug)
        #     else:
        #         if staff_form.errors:
        #             for field in staff_form:
        #                 for error in field.errors:
        #                     messages.add_message(request, messages.ERROR, error)
        #         return redirect('account:staff_create', request.user.email)
        # else:
        #     messages.add_message(request, messages.ERROR,
        #                          "You have no permission to add employee. Kindly contact your Manager or your Company Admin")
        #     return redirect('account:profile', request.user.email, request.user.company.company_slug)


# class CompanyUsers(View):
#     template = 'account/employees.html'

#     def get_object(self, user_id):
#         try:
#             user_id = force_text(urlsafe_base64_decode(user_id))
#             user = Staff.objects.get(pk=user_id)
#             return user
#         except Staff.DoesNotExist:
#             raise Http404

#     def get(self, request, company_slug):
#         staffs = Staff.objects.filter(company__company_slug=company_slug)
#         context = {
#             'staffs': staffs,
#         }
#         return render(request, template_name=self.template, context=context)


# class StaffProfile(View):
#     template = 'account/profile.html'

#     def get(self, request, company_slug, my_user):
#         company = Company.objects.get(company_slug=company_slug)
#         staff = Staff.objects.get(email=my_user)
#         staff_private_info, created = StaffPrivateInfo.objects.get_or_create(staff=staff)

#         company_users = Staff.objects.filter(company=company)
#         # company_dept = Department.objects.filter(company=company)
#         company_div = Division.objects.filter(company=company)
#         context = {
#             'user_company': company,
#             'staff': staff,
#             'staff_private_info': staff_private_info,
#             'company_users': company_users,
#             # 'company_dept': company_dept,
#             'company_div': company_div,
#         }
#         return render(request, template_name=self.template, context=context)


# class ActivateUserView(View):
#     template = 'account/activate_user.html'

#     def get_object(self, user_id):
#         try:
#             user_id = force_text(urlsafe_base64_decode(user_id))
#             user = Staff.objects.get(pk=user_id)
#             return user
#         except Staff.DoesNotExist:
#             raise Http404

#     def get(self, request, user_id, token, company_slug):
#         user = self.get_object(user_id)
#         validated = user_tokenizer.check_token(user, token)
#         if validated:
#             password_form = CompanyStaffSetPassword()
#             context = {
#                 'password_form': password_form
#             }
#             messages.add_message(request, messages.SUCCESS, "Staff Validated. Please set your password")
#             return render(request, template_name=self.template, context=context)
#         else:
#             context = {

#             }
#             messages.add_message(request, messages.ERROR,
#                                  "Staff cannot be validated. Please contact your company admin")
#             return render(request, template_name=self.template, context=context)

#     def post(self, request, user_id, token, company_slug):
#         password_form = CompanyStaffSetPassword(request.POST)
#         if password_form.is_valid():
#             password = password_form.cleaned_data['password']
#             confirm_password = password_form.cleaned_data['confirm_password']
#             staff = self.get_object(user_id)
#             staff.set_password(password)
#             staff.is_active = True
#             staff.save()
#             my_user = authenticate(request, email=staff.email, password=password)
#             login(request, my_user)

#             messages.add_message(request, messages.SUCCESS, "Login Successful")
#             return redirect('account:dashboard', request.user.email, request.user.company.company_slug)

#         else:
#             if password_form.errors:
#                 for field in password_form:
#                     for error in field.errors:
#                         messages.add_message(request, messages.ERROR, error)
#             return redirect('account:staff_set_password',
#                             kwargs={'company_slug': company_slug,
#                                     'user_id': user_id, 'token': token})



# def send_verification_email(request, staff_id, company_slug):
#     if request.method == 'POST':
#         if 'set_password' in request.POST:
#             staff = Staff.objects.get(pk=staff_id)
#             user_id = urlsafe_base64_encode(force_bytes(staff.pk))
#             token = user_tokenizer.make_token(staff)
#             employee_company = staff.company
#             employee_email = staff.email
#             company_slug = staff.company.company_slug
#             message = 'http://' + settings.MY_SERVER + reverse('account:staff_set_password',
#                                                                kwargs={'company_slug': company_slug,
#                                                                        'user_id': user_id, 'token': token})
#             new_employee_created.send(
#                 sender=staff,
#                 company=employee_company,
#                 message=message,
#                 email=employee_email,
#                 company_slug=company_slug,
#             )
#             next = request.POST.get('next', '/')
#             messages.add_message(request, messages.SUCCESS, "Activation Mail sent Successfully")
#             return redirect(next)


# class PasswordRestView(View):
#     template = 'account/password_reset_request.html'

#     def get(self, request):
#         request_password_reset_form = CompanyStaffResetPasswordRequest()
#         context = {
#             'request_password_reset_form': request_password_reset_form
#         }
#         return render(request, template_name=self.template, context=context)

#     def post(self, request):
#         request_password_reset_form = CompanyStaffResetPasswordRequest(request.POST)
#         if request_password_reset_form.is_valid():
#             email = request_password_reset_form.cleaned_data.get('email').lower()
#             try:
#                 my_staff = Staff.objects.get(email=email)
#                 company_slug = my_staff.company.company_slug
#                 user_id = urlsafe_base64_encode(force_bytes(my_staff.pk))
#                 token = user_tokenizer.make_token(my_staff)

#                 message = 'http://' + settings.MY_SERVER + reverse('account:staff_set_password',
#                                                                    kwargs={'company_slug': company_slug,
#                                                                            'user_id': user_id, 'token': token})
#                 new_employee_created.send(
#                     sender=my_staff,
#                     company=my_staff.company,
#                     message=message,
#                     email=my_staff.email,
#                     company_slug=company_slug,
#                     notification_type="RESET_PASSWORD",
#                 )
#                 messages.add_message(request, messages.SUCCESS, "A Password reset link as been sent to your email")
#                 return redirect(self.request.path_info)
#             except ObjectDoesNotExist:
#                 error = "User with this Email does not Exist"
#                 messages.add_message(request, messages.ERROR, error)
#                 return redirect(self.request.path_info)
#         else:
#             if request_password_reset_form.errors:
#                 for field in request_password_reset_form:
#                     for error in field.errors:
#                         messages.add_message(request, messages.ERROR, error)
#             return redirect(self.request.path_info)
    
    
    
    
    
    
    
    
    
    
# flow
# create user from dashboard, set role, user gets invitation and click 
# on link  - -feels user details (phone, password, fullname, position)
# account is activated, email is verified
# User logins in 




