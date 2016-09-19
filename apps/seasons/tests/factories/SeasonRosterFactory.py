import factory
from factory import django, post_generation

from seasons.models import AbstractSeasonRoster, HockeySeasonRoster


class AbstractSeasonRosterFactory(django.DjangoModelFactory):
    class Meta:
        model = AbstractSeasonRoster
        abstract = True

    season = factory.SubFactory('seasons.tests.SeasonFactory')
    team = factory.SubFactory('teams.tests.TeamFactory')
    default = False


class HockeySeasonRosterFactory(AbstractSeasonRosterFactory):
    class Meta:
        model = HockeySeasonRoster

    @post_generation
    def players(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for player in extracted:
                self.players.add(player)
