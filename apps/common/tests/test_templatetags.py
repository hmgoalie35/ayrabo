from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from common.templatetags.utils import get_past_seasons_nav_tab_url
from leagues.tests import LeagueFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory


class TestTemplateTagUtils(BaseTestCase):
    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(sport=self.ice_hockey, name='Long Island Amateur Hockey League')
        # Don't really care about the start/end dates here.
        self.past_season = SeasonFactory(league=self.liahl)

    def test_get_past_seasons_nav_tab_url_league(self):
        ctx = {'league': self.liahl, 'past_season': self.past_season}
        url = get_past_seasons_nav_tab_url(ctx, 'league')
        expected_url = reverse('leagues:seasons:schedule', kwargs={'slug': 'liahl', 'season_pk': self.past_season.pk})
        self.assertEqual(url, expected_url)

    def test_get_past_seasons_nav_tab_url_team(self):
        ctx = {'league': self.liahl, 'past_season': self.past_season}
        url = get_past_seasons_nav_tab_url(ctx, 'team')
        expected_url = ''
        self.assertEqual(url, expected_url)

    def test_get_past_seasons_nav_tab_url_none(self):
        ctx = {'league': self.liahl, 'past_season': self.past_season}
        url = get_past_seasons_nav_tab_url(ctx, 'invalid_profile_type')
        self.assertEqual(url, '')
