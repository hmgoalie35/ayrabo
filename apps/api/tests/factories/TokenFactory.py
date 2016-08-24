import factory
from factory import django
from rest_framework.authtoken.models import Token

from accounts.tests import UserFactory


class TokenFactory(django.DjangoModelFactory):
    class Meta:
        model = Token

    user = factory.SubFactory(UserFactory)
