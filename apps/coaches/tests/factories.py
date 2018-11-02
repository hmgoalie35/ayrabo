from factory import Faker, SubFactory, django

from coaches.models import Coach
from teams.tests import TeamFactory
from users.tests import UserFactory


class CoachFactory(django.DjangoModelFactory):
    user = SubFactory(UserFactory)
    position = Faker('random_element', elements=[position[0] for position in Coach.POSITIONS])
    team = SubFactory(TeamFactory)
    is_active = True

    class Meta:
        model = Coach
