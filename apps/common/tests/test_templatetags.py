from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from common.templatetags.utils import get_seasons_nav_tab_url
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory


class TemplateTagUtilsTests(BaseTestCase):
    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(sport=self.ice_hockey, name='Long Island Amateur Hockey League')
        # Don't really care about the start/end dates here.
        self.season = SeasonFactory(league=self.liahl)

    def test_get_seasons_nav_tab_url_league(self):
        ctx = {'league': self.liahl, 'season_dropdown_obj': self.season}
        url = get_seasons_nav_tab_url(ctx, 'league')
        expected_url = reverse('leagues:seasons:schedule', kwargs={'slug': 'liahl', 'season_pk': self.season.pk})
        self.assertEqual(url, expected_url)

    def test_get_seasons_nav_tab_url_team(self):
        division = DivisionFactory(league=self.liahl, name='Midget Minor AA')
        team = TeamFactory(division=division)
        ctx = {'league': self.liahl, 'season_dropdown_obj': self.season, 'team': team}
        url = get_seasons_nav_tab_url(ctx, 'team')
        expected_url = reverse('teams:seasons:schedule', kwargs={'team_pk': team.pk, 'season_pk': self.season.pk})
        self.assertEqual(url, expected_url)

    def test_get_seasons_nav_tab_url_none(self):
        ctx = {'league': self.liahl, 'season_dropdown_obj': self.season}
        url = get_seasons_nav_tab_url(ctx, 'invalid_profile_type')
        self.assertEqual(url, '')
