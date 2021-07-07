import string, random


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