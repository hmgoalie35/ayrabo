import random

import factory
from factory import django, fuzzy

from accounts.tests.factories.UserFactory import UserFactory
from players import models
from sports.tests.factories.SportFactory import SportFactory
from teams.tests.factories.TeamFactory import TeamFactory


def generate_jersey_number():
    return random.randint(0, 99)


class PlayerFactory(django.DjangoModelFactory):
    class Meta:
        model = models.Player
        abstract = True

    user = factory.SubFactory(UserFactory)
    sport = factory.SubFactory(SportFactory)
    team = factory.SubFactory(TeamFactory)
    jersey_number = factory.LazyFunction(generate_jersey_number)


class HockeyPlayerFactory(PlayerFactory):
    class Meta:
        model = models.HockeyPlayer

    position = fuzzy.FuzzyChoice([position[0] for position in models.HockeyPlayer.POSITIONS])
    handedness = fuzzy.FuzzyChoice([handedness[0] for handedness in models.HockeyPlayer.HANDEDNESS])
