import factory
from djmoney.money import Money

from accounts.models import Account



class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'accounts.Account'

    account_type = factory.Iterator([x[0] for x in Account.ACCOUNT_CHOICES])
    balance =  Money(1000, 'NGN')
    name = factory.Sequence(lambda n: 'account name {}'.format(n))