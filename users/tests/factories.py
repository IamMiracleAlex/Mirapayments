import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.User'

    first_name = factory.Sequence(lambda n: 'user{}'.format(n))
    email = factory.LazyAttribute(lambda obj: '%s@mirapayments.com' % obj.first_name)
    phone = factory.Sequence(lambda n: '0801234567{}'.format(n))
    password = factory.Sequence(lambda n: 'password{}'.format(n))
    is_superuser = False
    is_staff = False