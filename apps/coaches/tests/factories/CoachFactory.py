import factory
from factory import django, Faker

from accounts.tests import UserFactory
from coaches.models import Coach
from teams.tests import TeamFactory


class CoachFactory(django.DjangoModelFactory):
    class Meta:
        model = Coach

    user = factory.SubFactory(UserFactory)
    position = Faker('random_element', elements=[position[0] for position in Coach.POSITIONS])
    team = factory.SubFactory(TeamFactory)
    is_active = True
