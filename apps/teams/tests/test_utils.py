from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from sports.tests import SportFactory
from teams import utils
from teams.tests import TeamFactory
from teams.utils import get_team_detail_players_url, get_team_detail_schedule_url, get_team_detail_season_rosters_url


class UtilsTests(BaseTestCase):
    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(sport=self.ice_hockey, name='Long Island Amateur Hockey League')
        self.mm_aa = DivisionFactory(league=self.liahl, name='Midget Minor AA')
        self.icecats = TeamFactory(division=self.mm_aa, name='Green Machine IceCats')
        self.past_season, self.current_season, self.future_season = self.create_past_current_future_seasons(
            league=self.liahl
        )
        self.expected_team_detail_view_context = {
            'team_display_name': 'Green Machine IceCats - Midget Minor AA',
            'season': '',
            'schedule_link': '',
            'players_link': reverse('teams:players', kwargs={'team_pk': self.icecats.pk}),
            'season_rosters_link': '',
            'seasons': [self.future_season, self.current_season, self.past_season]
        }

    def test_get_team_detail_schedule_url(self):
        self.assertEqual(
            get_team_detail_schedule_url(self.icecats, self.past_season),
            reverse('teams:seasons:schedule', kwargs={
                'team_pk': self.icecats.pk,
                'season_pk': self.past_season.pk
            })
        )
        self.assertEqual(
            get_team_detail_schedule_url(self.icecats, self.current_season),
            reverse('teams:schedule', kwargs={'team_pk': self.icecats.pk})
        )
        self.assertEqual(
            get_team_detail_schedule_url(self.icecats, self.future_season),
            reverse('teams:seasons:schedule', kwargs={
                'team_pk': self.icecats.pk,
                'season_pk': self.future_season.pk
            })
        )

    def test_get_team_detail_players_url(self):
        self.assertEqual(
            get_team_detail_players_url(self.icecats),
            reverse('teams:players', kwargs={'team_pk': self.icecats.pk})
        )

    def test_get_team_detail_season_rosters_url(self):
        self.assertEqual(
            get_team_detail_season_rosters_url(self.icecats, self.past_season),
            reverse('teams:seasons:season_rosters-list', kwargs={
                'team_pk': self.icecats.pk,
                'season_pk': self.past_season.pk
            })
        )
        self.assertEqual(
            get_team_detail_season_rosters_url(self.icecats, self.current_season),
            reverse('teams:season_rosters:list', kwargs={'team_pk': self.icecats.pk})
        )
        self.assertEqual(
            get_team_detail_season_rosters_url(self.icecats, self.future_season),
            reverse('teams:seasons:season_rosters-list', kwargs={
                'team_pk': self.icecats.pk,
                'season_pk': self.future_season.pk
            })
        )

    def test_get_team_detail_view_context_current_season(self):
        result = utils.get_team_detail_view_context(self.icecats, season=self.current_season)
        kwargs = {'team_pk': self.icecats.pk}
        self.expected_team_detail_view_context.update({
            'season': self.current_season,
            'schedule_link': reverse('teams:schedule', kwargs=kwargs),
            'season_rosters_link': reverse('teams:season_rosters:list', kwargs=kwargs)
        })
        self.assertDictWithQuerySetEqual(result, self.expected_team_detail_view_context)

    def test_get_team_detail_view_context_past_season(self):
        kwargs = {'team_pk': self.icecats.pk, 'season_pk': self.past_season.pk}
        result = utils.get_team_detail_view_context(self.icecats, season=self.past_season)
        self.expected_team_detail_view_context.update({
            'season': self.past_season,
            'schedule_link': reverse('teams:seasons:schedule', kwargs=kwargs),
            'season_rosters_link': reverse('teams:seasons:season_rosters-list', kwargs=kwargs)
        })
        self.assertDictWithQuerySetEqual(result, self.expected_team_detail_view_context)

    def test_get_team_detail_view_context_future_season(self):
        kwargs = {'team_pk': self.icecats.pk, 'season_pk': self.future_season.pk}
        result = utils.get_team_detail_view_context(self.icecats, season=self.future_season)
        self.expected_team_detail_view_context.update({
            'season': self.future_season,
            'schedule_link': reverse('teams:seasons:schedule', kwargs=kwargs),
            'season_rosters_link': reverse('teams:seasons:season_rosters-list', kwargs=kwargs)
        })
        self.assertDictWithQuerySetEqual(result, self.expected_team_detail_view_context)
