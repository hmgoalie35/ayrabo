import factory
from allauth.account.models import EmailAddress
from factory import django

from users.tests import UserFactory


class EmailAddressFactory(django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    email = factory.lazy_attribute(lambda obj: obj.user.email)
    verified = True
    primary = True

    class Meta:
        model = EmailAddress
