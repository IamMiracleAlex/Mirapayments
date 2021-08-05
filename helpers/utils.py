import string, random

from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator  

from users.models import User


def generate_key(len, type):
    key = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(len))
    return '{}_{}'.format(type, key)

def generate_unique_key(klass, field, len=40, type=None):
	new_field = generate_key(len, type)

	if klass.objects.filter(**{field: new_field}).exists():
		return generate_key(klass, field)
	return new_field

def generate_random_number(len):
	return ''.join(random.choice(string.digits) for _ in range(len))

def generate_account_number(klass, field, len=10):
	new_field = generate_random_number(len)

	if klass.objects.filter(**{field: new_field}).exists():
		return generate_key(klass, field)
	return new_field


def validate_token(uidb64, token):
    is_valid = False

    try:
        id = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        is_valid = True
    
    return user, is_valid