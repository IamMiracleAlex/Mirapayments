import string, random
import os

import requests


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


# NOTE django money has a way of converting currencies too
def iscurrency_valid(currency):
    url = f"https://v6.exchangerate-api.com/v6/{os.environ['API_KEY']}/codes"
    res = requests.get(url)
    codes = res.json()["supported_codes"]
    valid_code = False
    for code in codes:
        if code[0].lower() == currency.lower():
            valid_code = True
            break
    return valid_code

def convert_currency(_from, _to, amount):
    url = f"https://v6.exchangerate-api.com/v6/{os.environ['API_KEY']}/pair/{_from.upper()}/{_to.upper()}/{amount}"
    res = requests.get(url)
    value = float(res.json()["conversion_result"])
    return value