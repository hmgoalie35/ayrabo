from factory import SubFactory, django

from scorekeepers.models import Scorekeeper
from sports.tests import SportFactory
from users.tests import UserFactory


class ScorekeeperFactory(django.DjangoModelFactory):
    user = SubFactory(UserFactory)
    sport = SubFactory(SportFactory)
    is_active = True

    class Meta:
        model = Scorekeeper
