from django.http import Http404

from ayrabo.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory
from seasons.utils import get_current_season_or_from_pk
from sports.tests import SportFactory


class UtilsTests(BaseTestCase):
    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(sport=self.ice_hockey, name='Long Island Amateur Hockey League')
        self.past_season, self.current_season, _ = self.create_past_current_future_seasons(league=self.liahl)

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
