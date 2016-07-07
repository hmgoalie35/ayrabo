import factory
from factory import django

from accounts.tests.factories.UserFactory import UserFactory
from divisions.tests.factories.DivisionFactory import DivisionFactory
from referees.models import Referee


class RefereeFactory(django.DjangoModelFactory):
    class Meta:
        model = Referee

    user = factory.SubFactory(UserFactory)
    division = factory.SubFactory(DivisionFactory)
