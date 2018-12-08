from ayrabo.utils.exceptions import SportNotConfiguredException
from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from seasons import utils
from seasons.tests import SeasonFactory
from sports.tests import SportFactory
from users.tests import UserFactory


class TestUtils(BaseTestCase):
    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(sport=self.ice_hockey, name='Long Island Amateur Hockey League')
        self.d1 = DivisionFactory(league=self.liahl, name='Division 1')
        self.d2 = DivisionFactory(league=self.liahl, name='Division 2')
        self.d3 = DivisionFactory(league=self.liahl, name='Division 3')
        self.d4 = DivisionFactory(league=self.liahl, name='Division 4')
        self.d5 = DivisionFactory(league=self.liahl, name='Division 5')

    def test_get_chunked_divisions(self):
        chunked_divisions = utils.get_chunked_divisions([self.d1, self.d2, self.d3, self.d4, self.d5])
        expected = [
            [self.d1, self.d2, self.d3, self.d4],
            [self.d5]
        ]
        self.assertListEqual(chunked_divisions, expected)

    def test_get_games_sport_dne(self):
        sport = SportFactory(name='Sport 1')
        season = SeasonFactory(league__sport=sport)
        with self.assertRaises(SportNotConfiguredException):
            utils.get_games(sport, season)

    def test_get_schedule_view_context(self):
        season = SeasonFactory(league=self.liahl)
        user = UserFactory()
        context = utils.get_schedule_view_context(user, self.ice_hockey, season)
        self.assertDictWithQuerySetEqual(context, {
            'active_tab': 'schedule',
            'season': season,
            'games': [],
            'has_games': False,
            'team_ids_managed_by_user': [],
            'is_scorekeeper': False,
            'sport': self.ice_hockey
        })
