from factory import SubFactory, django

from leagues.tests import LeagueFactory
from referees.models import Referee
from users.tests import UserFactory


class RefereeFactory(django.DjangoModelFactory):
    user = SubFactory(UserFactory)
    league = SubFactory(LeagueFactory)
    is_active = True

    class Meta:
        model = Referee
