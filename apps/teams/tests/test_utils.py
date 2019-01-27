from datetime import date, timedelta

from django.http import Http404
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory
from teams import utils
from teams.tests import TeamFactory
from teams.utils import get_season


class UtilsTests(BaseTestCase):
    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(sport=self.ice_hockey, name='Long Island Amateur Hockey League')
        self.mm_aa = DivisionFactory(league=self.liahl, name='Midget Minor AA')
        self.icecats = TeamFactory(division=self.mm_aa, name='Green Machine IceCats')
        today = date.today()
        self.current_season = SeasonFactory(league=self.liahl, start_date=today, end_date=today + timedelta(days=365))
        # Last year
        past_season_start_date = today - timedelta(days=365)
        past_season_end_date = today - timedelta(days=1)
        self.past_season = SeasonFactory(league=self.liahl, start_date=past_season_start_date,
                                         end_date=past_season_end_date)
        self.expected_team_detail_view_context = {
            'team_display_name': 'Green Machine IceCats - Midget Minor AA',
            'season': '',
            'schedule_link': '',
            'season_rosters_link': '',
            'past_seasons': [self.past_season]
        }

    def test_get_season_current_season(self):
        season = get_season(self.liahl, None)
        self.assertEqual(season, self.current_season)

    def test_get_season_past_season_pk_dne(self):
        with self.assertRaises(Http404):
            get_season(self.liahl, 100)

    def test_get_season_past_season_qs_filtered_by_league(self):
        with self.assertRaises(Http404):
            get_season(LeagueFactory(sport=self.ice_hockey), self.past_season.pk)

    def test_get_season_past_season(self):
        season = get_season(self.liahl, self.past_season.pk)
        self.assertEqual(season, self.past_season)

    def test_get_team_detail_view_context_current_season(self):
        result = utils.get_team_detail_view_context(self.icecats)
        self.expected_team_detail_view_context.update({
            'season': self.current_season,
            'schedule_link': reverse('teams:schedule', kwargs={'team_pk': self.icecats.pk}),
            'season_rosters_link': reverse('teams:season_rosters:list', kwargs={'team_pk': self.icecats.pk})
        })
        self.assertDictWithQuerySetEqual(result, self.expected_team_detail_view_context)

    def test_get_team_detail_view_context_past_season(self):
        result = utils.get_team_detail_view_context(self.icecats, season_pk=self.past_season.pk)
        self.expected_team_detail_view_context.update({
            'season': self.past_season,
            'schedule_link': reverse('teams:seasons:schedule',
                                     kwargs={'team_pk': self.icecats.pk, 'season_pk': self.past_season.pk}),
            'season_rosters_link': reverse('teams:season_rosters:list', kwargs={'team_pk': self.icecats.pk})
        })
        self.assertDictWithQuerySetEqual(result, self.expected_team_detail_view_context)
