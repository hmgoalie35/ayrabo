from django.shortcuts import reverse

from ayrabo.utils.testing import BaseTestCase
from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from divisions.tests import DivisionFactory
from games.tests import HockeyGameFactory
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from organizations.tests import OrganizationFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class AbstractLeagueDetailViewTestCase(BaseTestCase):
    def setUp(self):
        self.user = UserFactory()
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.nhl = LeagueFactory(name='National Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(league=self.liahl, name='Midget Minor AA')
        self.peewee = DivisionFactory(league=self.liahl, name='Pee Wee')
        self.atlantic = DivisionFactory(league=self.nhl, name='Atlantic')

        self.icecats_organization = OrganizationFactory(name='Green Machine IceCats', sport=self.ice_hockey)
        self.edge_organization = OrganizationFactory(name='Long Island Edge', sport=self.ice_hockey)
        self.rebels_organization = OrganizationFactory(name='Long Island Rebels', sport=self.ice_hockey)
        self.bruins_organization = OrganizationFactory(name='Boston Bruins', sport=self.ice_hockey)
        self.sabres_organization = OrganizationFactory(name='Buffalo Sabres', sport=self.ice_hockey)

        # Teams
        self.icecats_mm_aa = TeamFactory(
            name='Green Machine IceCats',
            division=self.mm_aa,
            organization=self.icecats_organization
        )
        self.icecats_peewee = TeamFactory(
            name='Green Machine IceCats',
            division=self.peewee,
            organization=self.icecats_organization
        )
        self.managers = [ManagerFactory(user=self.user, team=self.icecats_mm_aa)]
        self.edge_mm_aa = TeamFactory(
            name='Long Island Edge',
            division=self.mm_aa,
            organization=self.edge_organization
        )
        self.edge_peewee = TeamFactory(
            name='Long Island Edge',
            division=self.peewee,
            organization=self.edge_organization
        )

        self.rebels_mm_aa = TeamFactory(
            name='Long Island Rebels',
            division=self.mm_aa,
            organization=self.rebels_organization
        )
        self.rebels_peewee = TeamFactory(
            name='Long Island Rebels',
            division=self.peewee,
            organization=self.rebels_organization
        )
        self.bruins = TeamFactory(name='Boston Bruins', division=self.atlantic, organization=self.bruins_organization)
        self.sabres = TeamFactory(name='Buffalo Sabres', division=self.atlantic, organization=self.sabres_organization)

        self.teams = [
            self.icecats_mm_aa, self.icecats_peewee, self.edge_mm_aa, self.edge_peewee, self.rebels_mm_aa,
            self.rebels_peewee
        ]
        self.past_season, self.current_season, self.future_season = self.create_past_current_future_seasons(
            league=self.liahl,
            teams=self.teams
        )
        self.future_season.teams.clear()
        self.future_season.teams.add(self.icecats_mm_aa)


class LeagueDetailScheduleViewTests(AbstractLeagueDetailViewTestCase):
    url = 'leagues:schedule'

    def _create_game(self, home_team, away_team, season):
        return HockeyGameFactory(
            home_team=home_team,
            away_team=away_team,
            team=home_team,
            season=season,
            type=self.game_type,
            point_value=self.point_value
        )

    def setUp(self):
        super().setUp()
        self.game_type = GenericChoiceFactory(
            short_value='exhibition',
            long_value='Exhibition',
            type=GenericChoice.GAME_TYPE,
            content_object=self.ice_hockey
        )
        self.point_value = GenericChoiceFactory(
            short_value='2',
            long_value='2',
            type=GenericChoice.GAME_POINT_VALUE,
            content_object=self.ice_hockey
        )
        self.game1 = self._create_game(self.icecats_mm_aa, self.edge_mm_aa, self.current_season)
        self.game2 = self._create_game(self.icecats_mm_aa, self.rebels_mm_aa, self.current_season)
        self.game3 = self._create_game(self.icecats_peewee, self.edge_peewee, self.current_season)
        self.game4 = self._create_game(self.icecats_peewee, self.rebels_peewee, self.past_season)
        self.game5 = self._create_game(self.icecats_mm_aa, self.edge_mm_aa, self.past_season)
        # Game for another league (should be excluded)
        self.nhl_season = SeasonFactory(league=self.nhl)
        self._create_game(self.bruins, self.sabres, self.nhl_season)
        self.games = [self.game1, self.game2, self.game3]
        self.past_season_games = [self.game4, self.game5]
        self.login(user=self.user)

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
        self.assertEqual(context.get('season'), self.current_season)
        kwargs = {'slug': self.liahl.slug}
        self.assertEqual(context.get('schedule_link'), reverse('leagues:schedule', kwargs=kwargs))
        self.assertEqual(context.get('divisions_link'), reverse('leagues:divisions', kwargs=kwargs))
        self.assertIsNotNone(context.get('seasons'))
        self.assertEqual(context.get('current_season_page_url'), reverse('leagues:schedule', kwargs=kwargs))

        self.assertEqual(context.get('active_tab'), 'schedule')
        self.assertListEqual(list(context.get('games').order_by('id')), self.games)
        self.assertTrue(context.get('has_games'))

        self.assertListEqual(list(context.get('team_ids_managed_by_user')), team_ids_managed_by_user)
        self.assertFalse(context.get('is_scorekeeper'))
        self.assertEqual(context.get('sport'), self.ice_hockey)

    def test_get_past_season(self):
        url = reverse('leagues:seasons:schedule', kwargs={'slug': self.liahl.slug, 'season_pk': self.past_season.pk})
        response = self.client.get(url)
        team_ids_managed_by_user = [m.team_id for m in self.managers]
        context = response.context

        self.assert_200(response)
        self.assertTemplateUsed(response, 'leagues/league_detail_schedule.html')

        self.assertEqual(context.get('league'), self.liahl)
        self.assertEqual(context.get('season'), self.past_season)
        kwargs = {'slug': self.liahl.slug, 'season_pk': self.past_season.pk}
        self.assertEqual(context.get('schedule_link'), reverse('leagues:seasons:schedule', kwargs=kwargs))
        self.assertEqual(context.get('divisions_link'), reverse('leagues:seasons:divisions', kwargs=kwargs))
        self.assertIsNotNone(context.get('seasons'))
        self.assertEqual(
            context.get('current_season_page_url'),
            reverse('leagues:schedule', kwargs={'slug': self.liahl.slug})
        )

        self.assertEqual(context.get('active_tab'), 'schedule')
        self.assertListEqual(list(context.get('games').order_by('id')), self.past_season_games)
        self.assertTrue(context.get('has_games'))

        self.assertListEqual(list(context.get('team_ids_managed_by_user')), team_ids_managed_by_user)
        self.assertFalse(context.get('is_scorekeeper'))
        self.assertEqual(context.get('sport'), self.ice_hockey)

    def test_get_future_season(self):
        url = reverse('leagues:seasons:schedule', kwargs={'slug': self.liahl.slug, 'season_pk': self.future_season.pk})
        response = self.client.get(url)
        context = response.context
        self.assert_200(response)
        self.assertEqual(context.get('season'), self.future_season)


class LeagueDetailDivisionsViewTests(AbstractLeagueDetailViewTestCase):
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
        self.assertEqual(context.get('season'), self.current_season)
        kwargs = {'slug': self.liahl.slug}
        self.assertEqual(context.get('schedule_link'), reverse('leagues:schedule', kwargs=kwargs))
        self.assertEqual(context.get('divisions_link'), reverse('leagues:divisions', kwargs=kwargs))
        self.assertIsNotNone(context.get('seasons'))

        self.assertEqual(context.get('active_tab'), 'divisions')
        expected = [
            [self.d1, self.d2, self.d3, self.mm_aa],
            [self.peewee]
        ]
        self.assertListEqual(context.get('chunked_divisions'), expected)
        self.assertEqual(context.get('current_season_page_url'), reverse('leagues:divisions', kwargs=kwargs))
        self.assertEqual(context.get('header_text'), 'All Divisions')

    def test_get_past_season(self):
        url = reverse('leagues:seasons:divisions', kwargs={'slug': self.liahl.slug, 'season_pk': self.past_season.pk})
        response = self.client.get(url)
        context = response.context

        self.assertEqual(context.get('league'), self.liahl)
        self.assertEqual(context.get('season'), self.past_season)
        kwargs = {'slug': self.liahl.slug, 'season_pk': self.past_season.pk}
        self.assertEqual(context.get('schedule_link'), reverse('leagues:seasons:schedule', kwargs=kwargs))
        self.assertEqual(context.get('divisions_link'), reverse('leagues:seasons:divisions', kwargs=kwargs))
        self.assertIsNotNone(context.get('seasons'))

        self.assertEqual(context.get('active_tab'), 'divisions')
        self.assertListEqual(
            context.get('chunked_divisions'),
            [
                [self.mm_aa, self.peewee],
            ]
        )
        self.assertEqual(
            context.get('current_season_page_url'),
            reverse('leagues:divisions', kwargs={'slug': self.liahl.slug})
        )
        self.assertEqual(context.get('header_text'), f'{self.past_season} Divisions')

    def test_get_future_season(self):
        url = reverse('leagues:seasons:divisions', kwargs={'slug': self.liahl.slug, 'season_pk': self.future_season.pk})
        response = self.client.get(url)
        context = response.context
        self.assertEqual(context.get('season'), self.future_season)
        self.assertEqual(context.get('header_text'), f'{self.future_season} Divisions')
        self.assertListEqual(
            context.get('chunked_divisions'),
            [
                [self.mm_aa],
            ]
        )
