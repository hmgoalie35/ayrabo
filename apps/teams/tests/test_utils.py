from datetime import date, timedelta

from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory
from teams import utils
from teams.tests import TeamFactory


class UtilsTests(BaseTestCase):
    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(sport=self.ice_hockey, name='Long Island Amateur Hockey League')
        self.mm_aa = DivisionFactory(league=self.liahl, name='Midget Minor AA')
        self.icecats = TeamFactory(division=self.mm_aa, name='Green Machine IceCats')
        # Last year
        start_date = date.today() - timedelta(days=365)
        self.past_season = SeasonFactory(league=self.liahl, start_date=start_date,
                                         end_date=start_date + timedelta(days=2))

    def test_get_team_detail_view_context(self):
        result = utils.get_team_detail_view_context(self.icecats)
        self.assertDictWithQuerySetEqual(result, {
            'team_display_name': 'Green Machine IceCats - Midget Minor AA',
            'past_seasons': [self.past_season]
        })
