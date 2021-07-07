from operator import mod
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from djmoney.money import Money

from accounts.utils import generate_unique_key, generate_account_number
from accounts.exceptions import InsufficientBalance


class Account(models.Model):
    INDIVIDUAL = 'individual'
    CORPORATE = 'business'
    RELIGIOUS = 'religious'
    GOVERNMENT = 'government'
    NGO = 'ngo'
    ACCOUNT_CHOICES = (
        (INDIVIDUAL, INDIVIDUAL),
        (CORPORATE, CORPORATE),
        (RELIGIOUS, RELIGIOUS),
        (GOVERNMENT, GOVERNMENT),
        (NGO, NGO),
    )
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    public_key = models.CharField(max_length=50, unique=True, editable=False)
    account_type = models.CharField(choices=ACCOUNT_CHOICES, max_length=100)
    balance = MoneyField(max_digits=14, decimal_places=2, default_currency='NGN', default=0.0, validators=[MinMoneyValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account_number = models.IntegerField(unique=True, editable=False)
    name = models.CharField(max_length=200)

    class Meta:
        unique_together = ('user', 'account_type',)
        abstract = True

    def __str__(self):
        return "{}'s {} account".format(
            self.user, 
            self.get_account_type_display()
        )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.account_number = generate_account_number(Account, 'account_number', 10)
            self.public_key = generate_unique_key(Account, 'live_pk', 40)
        self.full_clean()
        super().save(*args, **kwargs)

    def sufficient_balance(self, amount):
        return self.balance.amount >= amount

    def valid_money(self, amount):
        if not isinstance(Money, amount):
           return False
        
        if self.balance.currency != amount.currency:
            return False
        return True    


    def deposit(self, amount):
        """
        Deposits a value to the account.
        Also creates a new transaction with the deposit value.
        """
        
        if self.valid_money(amount):

            self.transaction_set.create(
                amount=amount,
                current_balance=self.balance + amount
            )
            self.balance += amount
            self.save()
            return True
        return False    

    def withdraw(self, amount):
        """
        Withdraw's a value from the wallet.
        Also creates a new transaction with the withdraw
        value.
        Should the withdrawn amount is greater than the
        balance this wallet currently has, it raises an
        :mod:`InsufficientBalance` error. This exception
        inherits from :mod:`django.db.IntegrityError`. So
        that it automatically rolls-back during a
        transaction lifecycle.
        """
        if not self.valid_money(amount):
            return

        if not self.sufficient_balance(amount):
            return

        self.transaction_set.create(
            value=-amount,
            current_balance=self.balance - amount
        )
        self.current_balance -= amount
        self.save()

    def transfer(self, dest, amount):
        pass


class TestAccount(models.Model):
    INDIVIDUAL = 'individual'
    CORPORATE = 'business'
    RELIGIOUS = 'religious'
    GOVERNMENT = 'government'
    NGO = 'ngo'
    ACCOUNT_CHOICES = (
        (INDIVIDUAL, INDIVIDUAL),
        (CORPORATE, CORPORATE),
        (RELIGIOUS, RELIGIOUS),
        (GOVERNMENT, GOVERNMENT),
        (NGO, NGO),
    )
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    public_key = models.CharField(max_length=50, unique=True, editable=False)
    account_type = models.CharField(choices=ACCOUNT_CHOICES, max_length=100)
    balance = MoneyField(max_digits=14, decimal_places=2, default_currency='NGN', default=0.0, validators=[MinMoneyValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account_number = models.IntegerField(unique=True, editable=False)
    name = models.CharField(max_length=200)
    class Meta:
        unique_together = ('user', 'account_type',)
        abstract = True

    def __str__(self):
        return "{}'s {} account".format(
            self.user, 
            self.get_account_type_display()
        )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.account_number = generate_account_number(Account, 'account_number', 10)
            self.public_key = generate_unique_key(Account, 'live_pk', 40)
        self.full_clean()
        super().save(*args, **kwargs)

    def sufficient_balance(self, amount):
        return self.balance.amount >= amount

    def valid_money(self, amount):
        if not isinstance(Money, amount):
           return False
        
        if self.balance.currency != amount.currency:
            return False
        return True    


    def deposit(self, amount):
        """
        Deposits a value to the account.
        Also creates a new transaction with the deposit value.
        """
        
        if self.valid_money(amount):

            self.transaction_set.create(
                amount=amount,
                current_balance=self.balance + amount
            )
            self.balance += amount
            self.save()
            return True
        return False    

    def withdraw(self, amount):
        """
        Withdraw's a value from the wallet.
        Also creates a new transaction with the withdraw
        value.
        Should the withdrawn amount is greater than the
        balance this wallet currently has, it raises an
        :mod:`InsufficientBalance` error. This exception
        inherits from :mod:`django.db.IntegrityError`. So
        that it automatically rolls-back during a
        transaction lifecycle.
        """
        if not self.valid_money(amount):
            return

        if not self.sufficient_balance(amount):
            return

        self.transaction_set.create(
            value=-amount,
            current_balance=self.balance - amount
        )
        self.current_balance -= amount
        self.save()

    def transfer(self, dest, amount):
        pass

    def save(self, *args, **kwargs):
        if not self.pk:
            self.public_key = generate_unique_key(Account, 'test_pk', 40)
        self.full_clean()
        super().save(*args, **kwargs)

# class SubAccount(models.Model):
#     pass

# @receiver(post_save, sender=Account)
# def create_test_account(sender, instance, created, **kwargs):
#     if created:
#         TestAccount.objects.create(
#             user=instance.user,
#             account_type=instance.account_type,
#             balance=instance.balance,
#             sub_account=instance.sub_account, 
#             account_number=instance.account_number, 
#             name=instance.name,
#         )

