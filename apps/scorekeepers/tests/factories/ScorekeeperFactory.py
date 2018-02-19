import factory
from factory import django

from users.tests import UserFactory
from scorekeepers.models import Scorekeeper
from sports.tests import SportFactory


class ScorekeeperFactory(django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    sport = factory.SubFactory(SportFactory)
    is_active = True

    class Meta:
        model = Scorekeeper
