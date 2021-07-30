from django.contrib.auth.tokens import default_token_generator  
# from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(user):
	context = {
		'name': user.first_name,
		'uid': urlsafe_base64_encode(force_bytes(user.id)),
		'token': default_token_generator.make_token(user),
	}
	email = user.email
	message = render_to_string('users/verification_email.txt', context)
	subject = 'Verify Your Email'
	send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

def send_user_activation_mail(user, account_name):
	context = {
		'name': user.first_name,
		'uid': urlsafe_base64_encode(force_bytes(user.id)),
		'token': default_token_generator.make_token(user),
        'account_name': account_name
	}
	email = user.email
	message = render_to_string('users/activation_email.txt', context)
	subject = 'Activate Your Account'
	send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
