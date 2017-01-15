import factory
from factory import django, fuzzy

from accounts.tests import UserFactory
from players import models
from sports.tests import SportFactory
from teams.tests import TeamFactory


class PlayerFactory(django.DjangoModelFactory):
    class Meta:
        model = models.AbstractPlayer
        abstract = True

    user = factory.SubFactory(UserFactory)
    sport = factory.SubFactory(SportFactory)
    team = factory.SubFactory(TeamFactory)
    jersey_number = fuzzy.FuzzyChoice(range(0, 99))


class HockeyPlayerFactory(PlayerFactory):
    class Meta:
        model = models.HockeyPlayer

    sport = factory.SubFactory(SportFactory)
    position = fuzzy.FuzzyChoice([position[0] for position in models.HockeyPlayer.POSITIONS])
    handedness = fuzzy.FuzzyChoice([handedness[0] for handedness in models.HockeyPlayer.HANDEDNESS])


class BaseballPlayerFactory(PlayerFactory):
    class Meta:
        model = models.BaseballPlayer

    sport = factory.SubFactory(SportFactory)
    position = fuzzy.FuzzyChoice([position[0] for position in models.BaseballPlayer.POSITIONS])
    catches = fuzzy.FuzzyChoice([catches[0] for catches in models.BaseballPlayer.CATCHES])
    bats = fuzzy.FuzzyChoice([bats[0] for bats in models.BaseballPlayer.BATS])


class BasketballPlayerFactory(PlayerFactory):
    class Meta:
        model = models.BasketballPlayer

    sport = factory.SubFactory(SportFactory)
    position = fuzzy.FuzzyChoice([position[0] for position in models.BasketballPlayer.POSITIONS])
    shoots = fuzzy.FuzzyChoice([shoots[0] for shoots in models.BasketballPlayer.SHOOTS])
