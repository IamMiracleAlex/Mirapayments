* Currency and Money
This project uses django money to manage money and curreny
[django-money](https://github.com/django-money/django-money)

Token generation uses cryptography for maximum security, linux users might need to install the following packages

* Debian and Ubuntu:

```sudo apt-get install build-essential libssl-dev libffi-dev python3-dev python-dev```

* Fedora and RHEL-derivatives:

```sudo yum install gcc libffi-devel python-devel openssl-devel```

* Logs
This project stores database logs, request logs, etc
See [django-request](https://django-request.readthedocs.io/en/latest/index.html) for more informations

* Authentication
this project uses a customized version of [knox](https://github.com/James1345/django-rest-knox) to handle authentation of different environments