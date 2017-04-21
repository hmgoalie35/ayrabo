import factory
from factory import django, fuzzy

from accounts.tests import UserFactory
from coaches.models import Coach
from teams.tests import TeamFactory


class CoachFactory(django.DjangoModelFactory):
    class Meta:
        model = Coach

    user = factory.SubFactory(UserFactory)
    position = fuzzy.FuzzyChoice([position[0] for position in Coach.POSITIONS])
    team = factory.SubFactory(TeamFactory)
    is_active = True
