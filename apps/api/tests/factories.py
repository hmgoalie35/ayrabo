from factory import SubFactory, django
from rest_framework.authtoken.models import Token

from users.tests import UserFactory


class TokenFactory(django.DjangoModelFactory):
    user = SubFactory(UserFactory)

    class Meta:
        model = Token
