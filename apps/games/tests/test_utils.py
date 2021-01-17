import datetime

import pytz

from ayrabo.utils.exceptions import SportNotConfiguredException
from ayrabo.utils.testing import BaseTestCase
from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from divisions.tests import DivisionFactory
from games import utils
from games.tests import HockeyGameFactory
from games.utils import get_start_game_not_allowed_msg
from leagues.tests import LeagueFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class UtilsTests(BaseTestCase):
    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(sport=self.ice_hockey, name='Long Island Amateur Hockey League')

    def test_get_games_sport_dne(self):
        sport = SportFactory(name='Sport 1')
        season = SeasonFactory(league__sport=sport)
        with self.assertRaises(SportNotConfiguredException):
            utils.get_games(sport, season)

    def test_get_games_filter_by_team(self):
        division = DivisionFactory(name='Midget Minor AA', league=self.liahl)
        team = TeamFactory(division=division, name='Green Machine IceCats')
        t2 = TeamFactory(division=division, name='Long Island Rebels')
        t3 = TeamFactory(division=division, name='Dix Hills Hawks')
        game_type = GenericChoiceFactory(id=1, short_value='exhibition', long_value='Exhibition',
                                         type=GenericChoice.GAME_TYPE, content_object=self.ice_hockey)
        point_value = GenericChoiceFactory(id=2, short_value='2', long_value='2', type=GenericChoice.GAME_POINT_VALUE,
                                           content_object=self.ice_hockey)
        tz = 'US/Eastern'

        season_start = datetime.date.today()
        season = SeasonFactory(league=self.liahl, start_date=season_start)
        start_base = datetime.datetime.combine(season_start, datetime.time(hour=19, minute=0))
        start_base = pytz.timezone(tz).localize(start_base)

        g1_start = start_base + datetime.timedelta(weeks=1)
        game1 = HockeyGameFactory(home_team=team, away_team=t2, type=game_type, point_value=point_value, timezone=tz,
                                  season=season, start=g1_start)
        g2_start = g1_start + datetime.timedelta(days=1)
        game2 = HockeyGameFactory(home_team=t2, away_team=team, type=game_type, point_value=point_value, timezone=tz,
                                  season=season, start=g2_start)
        g3_start = g1_start + datetime.timedelta(weeks=1)
        HockeyGameFactory(home_team=t2, away_team=t3, type=game_type, point_value=point_value, timezone=tz,
                          season=season, start=g3_start)
        result = utils.get_games(self.ice_hockey, season, team=team)
        self.assertEqual(list(result), [game2, game1])

    def test_get_game_list_view_context(self):
        season = SeasonFactory(league=self.liahl)
        user = UserFactory()
        context = utils.get_game_list_view_context(user, self.ice_hockey, season)
        self.assertDictWithQuerySetEqual(context, {
            'active_tab': 'schedule',
            'season': season,
            'games': [],
            'has_games': False,
            'sport': self.ice_hockey,
            'game_authorizations': {},
        })

    def test_get_start_game_not_allowed_msg(self):
        self.assertEqual(
            get_start_game_not_allowed_msg(),
            'Games can only be started 30 minutes before the scheduled start time.'
        )
