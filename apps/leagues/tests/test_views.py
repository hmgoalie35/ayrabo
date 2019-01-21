from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from seasons.tests.test_views import AbstractScheduleViewTestCase, LeagueSeasonDetailViewTestCase
from sports.tests import SportFactory


class LeagueDetailScheduleViewTests(AbstractScheduleViewTestCase):
    url = 'leagues:schedule'

    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.format_url(slug=self.liahl.slug))

    def test_sport_not_configured(self):
        sport = SportFactory()
        league = LeagueFactory(sport=sport)
        self.assertSportNotConfigured(self.format_url(slug=league.slug))

    # GET
    def test_get(self):
        response = self.client.get(self.format_url(slug=self.liahl.slug))
        team_ids_managed_by_user = [m.team_id for m in self.managers]
        context = response.context
        self.assert_200(response)
        self.assertTemplateUsed(response, 'leagues/league_detail_schedule.html')
        self.assertEqual(context.get('league'), self.liahl)
        self.assertEqual(context.get('sport'), self.ice_hockey)
        self.assertEqual(context.get('active_tab'), 'schedule')
        self.assertEqual(context.get('season'), self.current_season)
        self.assertListEqual(list(context.get('team_ids_managed_by_user')), team_ids_managed_by_user)
        self.assertFalse(context.get('is_scorekeeper'))
        self.assertListEqual(list(context.get('games')), self.games)
        self.assertTrue(context.get('has_games'))
        self.assertIsNotNone(context.get('past_seasons'))


class LeagueDetailDivisionsViewTests(LeagueSeasonDetailViewTestCase):
    url = 'leagues:divisions'

    def setUp(self):
        super().setUp()
        self.login(user=self.user)

    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.format_url(slug=self.liahl.slug))

    # GET
    def test_get(self):
        self.d1 = DivisionFactory(league=self.liahl, name='Division 1')
        self.d2 = DivisionFactory(league=self.liahl, name='Division 2')
        self.d3 = DivisionFactory(league=self.liahl, name='Division 3')
        response = self.client.get(self.format_url(slug=self.liahl.slug))
        context = response.context
        self.assert_200(response)
        self.assertTemplateUsed('leagues/league_detail_divisions.html')
        self.assertEqual(context.get('league'), self.liahl)
        self.assertEqual(context.get('active_tab'), 'divisions')
        self.assertIsNotNone(context.get('past_seasons'))
        expected = [
            [self.d1, self.d2, self.d3, self.mm_aa],
            [self.peewee]
        ]
        self.assertListEqual(list(context.get('chunked_divisions')), expected)
