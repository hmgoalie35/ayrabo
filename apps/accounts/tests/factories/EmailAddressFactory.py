import factory
from allauth.account.models import EmailAddress
from factory import django

from users.tests.factories.UserFactory import UserFactory


class EmailAddressFactory(django.DjangoModelFactory):
    class Meta:
        model = EmailAddress

    user = factory.SubFactory(UserFactory)
    email = factory.lazy_attribute(lambda obj: obj.user.email)
    verified = True
    primary = True
