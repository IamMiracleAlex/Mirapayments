import factory

from accounts.models import Account


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'accounts.Account'

    user = factory.SubFactory('users.tests.factories.UserFactory')
    account_type = factory.Iterator([x[0] for x in Account.ACCOUNT_CHOICES])
    balance = factory.Sequence(lambda n: int(n))
    name = factory.Sequence(lambda n: 'account name {}'.format(n))