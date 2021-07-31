import factory


class AuthTokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'knox.AuthToken'

    account = factory.SubFactory('accounts.tests.factories.AccountFactory')
    user =  factory.SubFactory('users.tests.factories.UserFactory')