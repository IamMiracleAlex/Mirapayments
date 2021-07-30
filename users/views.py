from accounts.models import Account
from django.contrib.auth import authenticate, login
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth.tokens import default_token_generator  
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework import status

from knox.models import AuthToken

from users import serializers
from users.models import User
from helpers.mailers import send_verification_email
from helpers.api_response import SuccessResponse, FailureResponse


class LoginView(APIView):
    '''
    Login users
    POST: /users/login/
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
        login(request, user)

        user_logged_in.send(sender=request.user.__class__,
            request=request, user=request.user)    
        data = serializers.UserSerializer(user).data
        
        # instances = AuthToken.objects.filter(user=user)
        # token = instances.first()

        token, _ = AuthToken.objects.get_or_create(user=user)
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
        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
         
            data = serializer.data
            # do we really need to send the token on signup?
            # data['live_token'] = instance.live_token
            # data['test_token'] = instance.test_token
            send_verification_email(user)
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
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
  
        if user and default_token_generator.check_token(user, token):

            if user.email_verified:
                return SuccessResponse(detail='Your email has already been verified')
            
            user.email_verified = True
            user.save()
            return SuccessResponse(detail='Email verification was successful')

        else:
            return FailureResponse(detail='Email verification failed. Token is either invalid or expired')


		


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



    
    
    
class UserInvitationView(APIView):

    def post(self, request):
        '''
        Invite account user
        POST: /users/invite/
        '''

        serializer = serializers.UserInvitationSerializer(request.data)
        if serializer.is_valid():
            serializer.save()

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




