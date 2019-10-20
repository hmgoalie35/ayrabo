from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from common.templatetags.utils import get_seasons_nav_tab_url
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory


class TemplateTagUtilsTests(BaseTestCase):
    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(sport=self.ice_hockey, name='Long Island Amateur Hockey League')
        self.past_season, self.current_season, self.future_season = self.create_past_current_future_seasons(
            league=self.liahl
        )

    def test_get_seasons_nav_tab_url_league(self):
        ctx = {'league': self.liahl}
        ctx.update({'season_dropdown_obj': self.past_season})
        self.assertEqual(
            get_seasons_nav_tab_url(ctx, 'league'),
            reverse('leagues:seasons:schedule', kwargs={'slug': 'liahl', 'season_pk': self.past_season.pk})
        )
        ctx.update({'season_dropdown_obj': self.current_season})
        self.assertEqual(
            get_seasons_nav_tab_url(ctx, 'league'),
            reverse('leagues:schedule', kwargs={'slug': 'liahl'})
        )
        ctx.update({'season_dropdown_obj': self.future_season})
        self.assertEqual(
            get_seasons_nav_tab_url(ctx, 'league'),
            reverse('leagues:seasons:schedule', kwargs={'slug': 'liahl', 'season_pk': self.future_season.pk})
        )

    def test_get_seasons_nav_tab_url_team(self):
        division = DivisionFactory(league=self.liahl, name='Midget Minor AA')
        team = TeamFactory(division=division)
        ctx = {'team': team}
        ctx.update({'season_dropdown_obj': self.past_season})
        self.assertEqual(
            get_seasons_nav_tab_url(ctx, 'team'),
            reverse('teams:seasons:schedule', kwargs={'team_pk': team.pk, 'season_pk': self.past_season.pk})
        )
        ctx.update({'season_dropdown_obj': self.current_season})
        self.assertEqual(
            get_seasons_nav_tab_url(ctx, 'team'),
            reverse('teams:schedule', kwargs={'team_pk': team.pk})
        )
        ctx.update({'season_dropdown_obj': self.future_season})
        self.assertEqual(
            get_seasons_nav_tab_url(ctx, 'team'),
            reverse('teams:seasons:schedule', kwargs={'team_pk': team.pk, 'season_pk': self.future_season.pk})
        )

    def test_get_seasons_nav_tab_url_none(self):
        ctx = {'league': self.liahl, 'season_dropdown_obj': self.past_season}
        url = get_seasons_nav_tab_url(ctx, 'invalid_profile_type')
        self.assertEqual(url, '')
