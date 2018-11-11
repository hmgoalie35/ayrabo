import datetime

from factory import LazyAttribute, LazyFunction, Sequence, SubFactory, django, post_generation

from leagues.tests import LeagueFactory
from seasons.models import AbstractSeasonRoster, HockeySeasonRoster
from seasons.models import Season
from users.tests import UserFactory


class SeasonFactory(django.DjangoModelFactory):
    start_date = LazyFunction(datetime.date.today)
    end_date = LazyAttribute(lambda obj: obj.start_date + datetime.timedelta(days=365))
    league = SubFactory(LeagueFactory)

    class Meta:
        model = Season

    @post_generation
    def teams(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for team in extracted:
                self.teams.add(team)


class AbstractSeasonRosterFactory(django.DjangoModelFactory):
    name = Sequence(lambda x: 'Season Roster {}'.format(x))
    season = SubFactory('seasons.tests.SeasonFactory')
    team = SubFactory('teams.tests.TeamFactory')
    default = False
    created_by = SubFactory(UserFactory)

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
