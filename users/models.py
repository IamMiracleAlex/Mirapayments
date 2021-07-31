from django.db import models
from django.contrib.auth.models import AbstractUser

from users.managers import CustomUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=25, default='', blank=True)
    email_verified = models.BooleanField(default=False)
    # country = models.CharField(max_length=150, default='nigeria')
    send_notificatioens = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    accounts = models.ManyToManyField('accounts.Account')


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __str__(self):
        return self.email



# class Business(models.Model):
#     name = models.CharField(max_length=250)
#     merchant_id = models.CharField(max_length=10)



# class Role(models.Model): use Role?
#     role = models.CharField(max_length=25, default='Admin')


#     def __str__(self):
#         return self.user_type

# class Compliance(models.Model):
#     pass