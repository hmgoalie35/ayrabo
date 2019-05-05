import datetime

import pytz

from common.tests import GenericChoiceFactory
from divisions.tests import DivisionFactory
from ayrabo.utils.testing import BaseAPITestCase
from games.tests import HockeyGameFactory
from leagues.tests import LeagueFactory
from players.tests import HockeyPlayerFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory
from ..serializers import HockeyGameRosterSerializer


class AbstractGameRosterSerializerTests(BaseAPITestCase):
    # Testing functionality via this serializer
    serializer_class = HockeyGameRosterSerializer

    def _create_players(self, ids, team, sport):
        players = []
        for i in ids:
            players.append(HockeyPlayerFactory(id=i, team=team, sport=sport))
        return players

    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)

        self.home_team = TeamFactory(id=1, name='Green Machine IceCats', division=self.mm_aa)
        self.home_players = self._create_players([1, 2, 3, 4, 5], self.home_team, self.ice_hockey)
        HockeyPlayerFactory(id=11, team=self.home_team, is_active=False)
        self.away_team = TeamFactory(id=2, name='Aviator Gulls', division=self.mm_aa)
        self.away_players = self._create_players([6, 7, 8, 9, 10], self.away_team, self.ice_hockey)
        HockeyPlayerFactory(id=15, team=self.away_team, is_active=False)

        self.game_type = GenericChoiceFactory(short_value='exhibition', long_value='Exhibition', type='game_type',
                                              content_object=self.ice_hockey)
        self.point_value = GenericChoiceFactory(short_value='2', long_value='2', type='game_point_value',
                                                content_object=self.ice_hockey)

        timezone = 'US/Eastern'
        us_eastern = pytz.timezone(timezone)

        self.season_start = datetime.date(month=12, day=27, year=2017)
        self.season = SeasonFactory(league=self.liahl, start_date=self.season_start)

        self.start = datetime.datetime(month=12, day=27, year=2017, hour=19, minute=0)
        self.end = self.start + datetime.timedelta(hours=3)
        self.game = HockeyGameFactory(home_team=self.home_team, team=self.home_team, away_team=self.away_team,
                                      type=self.game_type, point_value=self.point_value,
                                      start=us_eastern.localize(self.start), end=us_eastern.localize(self.end),
                                      timezone=timezone, season=self.season, status='scheduled')
        self.serializer = self.serializer_class(instance=self.game)

    def test_home_players_qs(self):
        qs = self.serializer.fields['home_players'].child_relation.queryset
        self.assertListEqual(list(qs.values_list('id', flat=True)), [5, 4, 3, 2, 1])

    def test_away_players_qs(self):
        qs = self.serializer.fields['away_players'].child_relation.queryset
        self.assertListEqual(list(qs.values_list('id', flat=True)), [10, 9, 8, 7, 6])
