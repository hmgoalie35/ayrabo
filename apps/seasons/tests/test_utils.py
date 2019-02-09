from django.http import Http404

from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from seasons import utils
from seasons.utils import get_current_season_or_from_pk
from sports.tests import SportFactory


class UtilsTests(BaseTestCase):
    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(sport=self.ice_hockey, name='Long Island Amateur Hockey League')
        self.d1 = DivisionFactory(league=self.liahl, name='Division 1')
        self.d2 = DivisionFactory(league=self.liahl, name='Division 2')
        self.d3 = DivisionFactory(league=self.liahl, name='Division 3')
        self.d4 = DivisionFactory(league=self.liahl, name='Division 4')
        self.d5 = DivisionFactory(league=self.liahl, name='Division 5')
        self.past_season, self.current_season, _ = self.create_past_current_future_seasons(league=self.liahl)

    def test_get_chunked_divisions(self):
        chunked_divisions = utils.get_chunked_divisions([self.d1, self.d2, self.d3, self.d4, self.d5])
        expected = [
            [self.d1, self.d2, self.d3, self.d4],
            [self.d5]
        ]
        self.assertListEqual(chunked_divisions, expected)

    def test_get_current_season_or_from_pk_current_season(self):
        season = get_current_season_or_from_pk(self.liahl, None)
        self.assertEqual(season, self.current_season)

    def test_get_current_season_or_from_pk_past_season_pk_dne(self):
        with self.assertRaises(Http404):
            get_current_season_or_from_pk(self.liahl, 100)

    def test_get_current_season_or_from_pk_past_season_qs_filtered_by_league(self):
        with self.assertRaises(Http404):
            get_current_season_or_from_pk(LeagueFactory(sport=self.ice_hockey), self.past_season.pk)

    def test_get_current_season_or_from_pk_past_season(self):
        season = get_current_season_or_from_pk(self.liahl, self.past_season.pk)
        self.assertEqual(season, self.past_season)
