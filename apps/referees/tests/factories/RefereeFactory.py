import factory
from factory import django

from users.tests import UserFactory
from leagues.tests import LeagueFactory
from referees.models import Referee


class RefereeFactory(django.DjangoModelFactory):
    class Meta:
        model = Referee

    user = factory.SubFactory(UserFactory)
    league = factory.SubFactory(LeagueFactory)
    is_active = True
