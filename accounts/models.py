from django.core import validators
from django.db import models

from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator

# from utils.tools import generate_unique_id


class Account(models.Model):

    INDIVIDUAL = 'individual'
    CORPORATE = 'corporate'
    NGO = 'ngo'
    ACCOUNT_CHOICES = (
        (INDIVIDUAL, INDIVIDUAL),
        (CORPORATE, CORPORATE),
        (NGO, NGO)
    )
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    public_id = models.CharField(max_length=50, unique=True, editable=False)
    account_type = models.PositiveSmallIntegerField(choices=ACCOUNT_CHOICES)
    balance = MoneyField(max_digits=14, decimal_places=2, default_currency='NGN', validators=[MinMoneyValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'account_type',)

    def __str__(self):
        return "{}'s {} account".format(
            self.user, 
            self.get_account_type_display()
        )

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         self.public_id = generate_unique_id(Account, 'public_id', 19)
    #     super(Account, self).save(*args, **kwargs)


    def sufficient_balance(self, amount):
        return self.balance.amount >= amount

    def deposit(self, value):
        """Deposits a value to the wallet.
        Also creates a new transaction with the deposit
        value.
        """
        self.transaction_set.create(
            value=value,
            running_balance=self.current_balance + value
        )
        self.current_balance += value
        self.save()

    def withdraw(self, value):
        """Withdraw's a value from the wallet.
        Also creates a new transaction with the withdraw
        value.
        Should the withdrawn amount is greater than the
        balance this wallet currently has, it raises an
        :mod:`InsufficientBalance` error. This exception
        inherits from :mod:`django.db.IntegrityError`. So
        that it automatically rolls-back during a
        transaction lifecycle.
        """
        if value > self.current_balance:
            raise Exception('This wallet has insufficient balance.')

        self.transaction_set.create(
            value=-value,
            running_balance=self.current_balance - value
        )
        self.current_balance -= value
        self.save()

    def transfer(self, wallet, value):
        """Transfers an value to another wallet.
        Uses `deposit` and `withdraw` internally.
        """
        self.withdraw(value)
        wallet.deposit(value)        