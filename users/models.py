from django.db import models
from django.contrib.auth.models import AbstractUser

from utils.tools import generate_unique_key
from users.managers import CustomUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, default='', blank=True)
    email_verified = models.BooleanField(default=False)
    # refer_code = models.CharField(
    #     max_length=15,
    #     unique=True,
    #     editable=False,
    # )
    # referer = models.ForeignKey(
    #     'self', 
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,
    #     related_name='referrals'
    # )
    send_notificatioens = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
  
    # is_live = models.models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __str__(self):
        return "{} {} - {}".format(self.first_name, self.last_name, self.email)

   
# class Compliance(models.Model):
#     pass