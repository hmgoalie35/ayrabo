import factory
from factory import django, post_generation

from accounts.tests import UserFactory
from seasons.models import AbstractSeasonRoster, HockeySeasonRoster


class AbstractSeasonRosterFactory(django.DjangoModelFactory):
    class Meta:
        model = AbstractSeasonRoster
        abstract = True

    season = factory.SubFactory('seasons.tests.SeasonFactory')
    team = factory.SubFactory('teams.tests.TeamFactory')
    default = False
    name = factory.Sequence(lambda x: 'Season Roster {}'.format(x))
    created_by = factory.SubFactory(UserFactory)

    @post_generation
    def full_clean(self, obj, extracted, **kwargs):
        self.full_clean()


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
