# Local Setup
1.  clone the repository
2.  create a virtual environment running python 3.8 (or above)
    https://realpython.com/python-virtual-environments-a-primer/#using-virtual-environments

3.  cd into the root of the django project (i.e the path containing manage.py)
4.  install requirements `pip install -r requirements.txt`
5.  Set up your environment variables using any credentials of your choice 
    or use the available defaults present in mirapayment/settings.py
6.  Create a local postgres instance (or use an existing one)
7.  Modiy the database credentials in settings to match yours (mirapayments/settings.py)
8.  run `python manage.py migrate` to create database tables
9.  run `python manage.py createsuperuser` to create a superuser(An initial user that has access to the admin site)
10. run `python manage.py populate_db` to populate the database with initial data
11. run `python manage.py runserver` to start the development server

The application should now be running on port 8000 (localhost:8000)
admin site available at localhost:8000/admin

# Development:
1. If your update requires a third party library to function, endeavour to update the `requirements.txt` file and add a comment of what the package does.
 Ensure only needed libraries are added and remove a library no longer in use
    from requirements to avoid unnecsaary dependencies

2. If your update requires change in the database, endeavour to generate migrations locally before pushing
    with `python manage.py makemigrations`. Test applying migrations locally and fix possible errors.

3. Provide docstrings and comments that adequately describes your operation/aim/usage

4. To schedule an operation,
    See `Celery` section below

# Currency and Money
This project uses django money to manage money and curreny
[django-money](https://github.com/django-money/django-money)


# Logs
This project stores error database logs, request logs, celery task results, etc
See [django-request](https://django-request.readthedocs.io/en/latest/index.html) for more informations
- Logs are scheduled to be cleared at intervals

# Authentication
this project uses a customized version of [knox](https://github.com/James1345/django-rest-knox) to handle authentation of different environments

# Using Celery
Please see https://docs.celeryproject.org/en/stable/index.html for more information.

-  Startup Celery worker to receive tasks:

`celery -A mirapayments worker -l info`

-  Startup Celery task scheduler:

`celery -A mirapayments beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`

or use

`celery -A mirapayments beat -l info`

-  To create an async task, do:
```
from celery import shared_task

@shared_task
def funx_name(x, y):
    return x + y
```

-  To create a scheduled task  
place the function in `<app_name>/schedules/<task_namey>.py/handle`

-  Add the task to `mirapayments/celery.py`

-  Add the module to celery imports in `mirapayments/settings.py`
