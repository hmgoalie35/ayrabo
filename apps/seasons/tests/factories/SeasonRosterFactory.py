import factory
from factory import django, post_generation

from seasons.models import AbstractSeasonRoster, HockeySeasonRoster
from users.tests import UserFactory


class AbstractSeasonRosterFactory(django.DjangoModelFactory):
    name = factory.Sequence(lambda x: 'Season Roster {}'.format(x))
    season = factory.SubFactory('seasons.tests.SeasonFactory')
    team = factory.SubFactory('teams.tests.TeamFactory')
    default = False
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = AbstractSeasonRoster
        abstract = True

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
