import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from divisions.tests import DivisionFactory
from games.tests import HockeyGameFactory
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from organizations.tests import OrganizationFactory
from players.tests import HockeyPlayerFactory
from seasons.tests import HockeySeasonRosterFactory
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from teams.models import Team
from teams.tests import TeamFactory
from users.tests import UserFactory


class BulkUploadTeamsViewTests(BaseTestCase):
    url = 'bulk_upload_teams'

    def setUp(self):
        self.url = self.format_url()
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.test_file_path = os.path.join(settings.BASE_DIR, 'static', 'csv_examples')
        self.user = UserFactory(email=self.email, password=self.password, is_staff=True)

    def test_post_valid_csv(self):
        ice_hockey = SportFactory(name='Ice Hockey')
        liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=ice_hockey)
        DivisionFactory(name='10U Milner', league=liahl)
        OrganizationFactory(name='Green Machine IceCats', sport=ice_hockey)
        self.login(email=self.email, password=self.password)
        with open(os.path.join(self.test_file_path, 'bulk_upload_teams_example.csv')) as f:
            response = self.client.post(self.url, {'file': f}, follow=True)
            self.assertHasMessage(response, 'Successfully created 1 team object(s)')
            self.assertEqual(Team.objects.count(), 1)

    def test_post_invalid_csv(self):
        self.login(email=self.email, password=self.password)
        content = b'name, website, division, organization\n\na,b,c,d'
        f = SimpleUploadedFile('test.csv', content)
        response = self.client.post(self.url, {'file': f}, follow=True)
        self.assertEqual(Team.objects.count(), 0)
        self.assertFormsetError(response, 'formset', 0, 'division',
                                ['Select a valid choice. That choice is not one of the available choices.'])
        self.assertFormsetError(response, 'formset', 0, 'organization',
                                ['Select a valid choice. That choice is not one of the available choices.'])


class TeamDetailScheduleViewTests(BaseTestCase):
    url = 'teams:schedule'

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
        self.user = UserFactory()
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(league=self.liahl, name='Midget Minor AA')

        self.icecats_organization = OrganizationFactory(name='Green Machine IceCats', sport=self.ice_hockey)
        self.edge_organization = OrganizationFactory(name='Long Island Edge', sport=self.ice_hockey)
        self.rebels_organization = OrganizationFactory(name='Long Island Rebels', sport=self.ice_hockey)

        # Teams
        self.icecats_mm_aa = TeamFactory(
            name='Green Machine IceCats',
            division=self.mm_aa,
            organization=self.icecats_organization
        )
        self.managers = [ManagerFactory(user=self.user, team=self.icecats_mm_aa)]
        self.edge_mm_aa = TeamFactory(
            name='Long Island Edge',
            division=self.mm_aa,
            organization=self.edge_organization
        )
        self.rebels_mm_aa = TeamFactory(
            name='Long Island Rebels',
            division=self.mm_aa,
            organization=self.rebels_organization
        )

        self.past_season, self.current_season, self.future_season = self.create_past_current_future_seasons(
            league=self.liahl
        )

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

        self.formatted_url = self.format_url(team_pk=self.icecats_mm_aa.pk)
        self.login(user=self.user)

    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.formatted_url)

    def test_sport_not_configured(self):
        # Note no season has been configured for this team's league, so the current season will be None.
        team = TeamFactory()
        self.assertSportNotConfigured(self.format_url(team_pk=team.pk))

    # GET
    def test_get(self):
        response = self.client.get(self.formatted_url)
        context = response.context
        team_ids_managed_by_user = [m.team_id for m in self.managers]

        self.assert_200(response)
        self.assertTemplateUsed('teams/team_detail_schedule.html')

        self.assertEqual(context.get('team_display_name'), 'Green Machine IceCats - Midget Minor AA')
        self.assertEqual(context.get('season'), self.current_season)
        self.assertEqual(context.get('schedule_link'), self.formatted_url)
        self.assertEqual(
            context.get('season_rosters_link'),
            reverse('teams:season_rosters:list', kwargs={'team_pk': self.icecats_mm_aa.pk})
        )
        self.assertIsNotNone(context.get('seasons'))
        self.assertEqual(context.get('current_season_page_url'), self.formatted_url)
        self.assertTrue(context.get('can_create_game'))

        self.assertEqual(context.get('active_tab'), 'schedule')
        self.assertListEqual(list(context.get('games')), [self.game2, self.game1])
        self.assertTrue(context.get('has_games'))

        self.assertListEqual(list(context.get('team_ids_managed_by_user')), team_ids_managed_by_user)
        self.assertFalse(context.get('is_scorekeeper'))
        self.assertEqual(context.get('sport'), self.ice_hockey)

    def test_get_past_season(self):
        kwargs = {'team_pk': self.icecats_mm_aa.pk, 'season_pk': self.past_season.pk}
        url = reverse('teams:seasons:schedule', kwargs=kwargs)
        response = self.client.get(url)
        context = response.context

        self.assert_200(response)
        self.assertTemplateUsed('teams/team_detail_schedule.html')

        self.assertEqual(context.get('season'), self.past_season)
        self.assertEqual(context.get('schedule_link'), url)
        self.assertEqual(
            context.get('season_rosters_link'),
            reverse('teams:seasons:season_rosters-list', kwargs=kwargs)
        )
        self.assertIsNotNone(context.get('seasons'))

        # The user is a manager for this team, but the season is expired.
        self.assertFalse(context.get('can_create_game'))
        self.assertFalse(context.get('has_games'))

    def test_get_future_season(self):
        response = self.client.get('teams:seasons:schedule', kwargs={
            'team_pk': self.icecats_mm_aa.pk,
            'season_pk': self.future_season.pk
        })

        context = response.context
        self.assertEqual(context.get('season'), self.future_season)
        self.assertTrue(context.get('can_create_game'))


class TeamDetailSeasonRostersViewTests(BaseTestCase):
    url = 'teams:season_rosters:list'

    def setUp(self):
        self.user = UserFactory()

        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)
        self.icecats = TeamFactory(name='Green Machine IceCats', division=self.mm_aa)
        self.past_season, self.current_season, self.future_season = self.create_past_current_future_seasons(self.liahl)

        self.hockey_sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.MANAGER)
        self.hockey_manager = ManagerFactory(user=self.user, team=self.icecats)

        self.hockey_players = HockeyPlayerFactory.create_batch(5, sport=self.ice_hockey, team=self.icecats)
        self.formatted_url = self.format_url(team_pk=self.icecats.pk)

        self.sr1 = HockeySeasonRosterFactory(name='SR1', season=self.current_season, team=self.icecats)
        self.sr2 = HockeySeasonRosterFactory(name='SR2', season=self.current_season, team=self.icecats)
        self.sr3 = HockeySeasonRosterFactory(name='SR3', season=self.current_season, team=self.icecats)
        self.sr4 = HockeySeasonRosterFactory(name='SR4', season=self.current_season, team=self.icecats)
        self.sr5 = HockeySeasonRosterFactory(season=self.past_season, team=self.icecats)

        self.login(user=self.user)

    # General
    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.formatted_url)

    def test_sport_not_configured(self):
        team = TeamFactory()
        self.assertSportNotConfigured(self.format_url(team_pk=team.pk))

    def test_can_user_list_season_rosters_not_manager(self):
        team = TeamFactory(division=self.mm_aa)
        response = self.client.get(self.format_url(team_pk=team.pk))
        context = response.context
        self.assertFalse(context.get('can_user_list'))
        self.assertQuerysetEqual(context.get('season_rosters'), [])

    def test_can_user_list_season_rosters_not_active_manager(self):
        self.hockey_manager.is_active = False
        self.hockey_manager.save()
        response = self.client.get(self.formatted_url)
        context = response.context
        self.assertFalse(context.get('can_user_list'))
        self.assertQuerysetEqual(context.get('season_rosters'), [])

    # GET
    def test_get(self):
        response = self.client.get(self.formatted_url)
        context = response.context

        self.assert_200(response)
        self.assertTemplateUsed(response, 'teams/team_detail_season_rosters.html')

        self.assertEqual(context.get('team_display_name'), 'Green Machine IceCats - Midget Minor AA')
        self.assertEqual(context.get('season'), self.current_season)
        self.assertIsNotNone(context.get('seasons'))

        # Only includes season rosters for the current season.
        self.assertListEqual(list(context.get('season_rosters')), [self.sr1, self.sr2, self.sr3, self.sr4])
        self.assertTrue(context.get('has_season_rosters'))
        self.assertEqual(context.get('active_tab'), 'season_rosters')
        self.assertTrue(context.get('can_user_list'))
        self.assertTrue(context.get('can_create_season_roster'))
        self.assertEqual(context.get('current_season_page_url'), self.formatted_url)

    def test_get_past_season(self):
        kwargs = {'team_pk': self.icecats.pk, 'season_pk': self.past_season.pk}
        url = reverse('teams:seasons:season_rosters-list', kwargs=kwargs)
        response = self.client.get(url)
        context = response.context

        self.assert_200(response)
        self.assertTemplateUsed('teams/team_detail_season_rosters.html')

        self.assertEqual(context.get('season'), self.past_season)
        self.assertIsNotNone(context.get('seasons'))

        self.assertListEqual(list(context.get('season_rosters')), [self.sr5])
        self.assertTrue(context.get('has_season_rosters'))
        self.assertEqual(context.get('schedule_link'), reverse('teams:seasons:schedule', kwargs=kwargs))
        self.assertEqual(context.get('season_rosters_link'), url)
        self.assertFalse(context.get('can_create_season_roster'))


class TeamDetailPlayersViewTests(BaseTestCase):
    url = 'teams:players'

    def setUp(self):
        self.user = UserFactory()

        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(sport=self.ice_hockey, name='Long Island Amateur Hockey League')
        self.mm_aa = DivisionFactory(league=self.liahl, name='Midget Minor AA')
        self.icecats_mm_aa = TeamFactory(division=self.mm_aa, name='Green Machine IceCats')
        self.edge_mm_aa = TeamFactory(division=self.mm_aa, name='Long Island Edge')
        self.p1 = HockeyPlayerFactory(team=self.icecats_mm_aa, sport=self.ice_hockey)
        self.p2 = HockeyPlayerFactory(team=self.icecats_mm_aa, sport=self.ice_hockey)
        self.p3 = HockeyPlayerFactory(team=self.icecats_mm_aa, sport=self.ice_hockey)
        self.p4 = HockeyPlayerFactory(team=self.icecats_mm_aa, sport=self.ice_hockey)
        self.p5 = HockeyPlayerFactory(team=self.icecats_mm_aa, sport=self.ice_hockey, is_active=False)
        self.p6 = HockeyPlayerFactory(team=self.edge_mm_aa, sport=self.ice_hockey)
        _, self.current_season, _ = self.create_past_current_future_seasons(self.liahl)

        self.formatted_url = self.format_url(team_pk=self.icecats_mm_aa.pk)
        self.login(user=self.user)

    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.formatted_url)

    def test_sport_not_configured(self):
        team = TeamFactory()
        self.assertSportNotConfigured(self.format_url(team_pk=team.pk))

    # GET
    def test_get(self):
        response = self.client.get(self.formatted_url)
        context = response.context

        self.assert_200(response)
        self.assertTemplateUsed('teams/team_detail_players.html')

        # Don't need to go crazy and test that everything from get_team_detail_view_context is here.
        self.assertEqual(context.get('team_display_name'), 'Green Machine IceCats - Midget Minor AA')
        self.assertEqual(context.get('season'), self.current_season)
        self.assertIsNotNone(context.get('seasons'))

        self.assertListEqual(context.get('columns'), ['Jersey Number', 'Name', 'Position', 'Handedness'])
        self.assertListEqual(list(context.get('players')), [self.p4, self.p3, self.p2, self.p1])
        self.assertTrue(context.get('has_players'))
        self.assertEqual(context.get('header_text'), 'All Players')
        self.assertEqual(context.get('sport'), self.ice_hockey)
        self.assertEqual(context.get('active_tab'), 'players')

    def test_get_no_players(self):
        team = TeamFactory(division=self.mm_aa)
        response = self.client.get(self.format_url(team_pk=team.pk))
        context = response.context

        self.assertListEqual(context.get('columns'), ['Jersey Number', 'Name'])
        self.assertListEqual(list(context.get('players')), [])
        self.assertFalse(context.get('has_players'))
