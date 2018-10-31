from allauth.account.models import EmailAddress
from factory import LazyAttribute, SubFactory, django

from users.tests import UserFactory


class EmailAddressFactory(django.DjangoModelFactory):
    user = SubFactory(UserFactory)
    email = LazyAttribute(lambda obj: obj.user.email)
    verified = True
    primary = True

    class Meta:
        model = EmailAddress
