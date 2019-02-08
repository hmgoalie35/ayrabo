from datetime import date, timedelta

from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from coaches.tests import CoachFactory
from common.tests import GenericChoiceFactory
from divisions.tests import DivisionFactory
from games.tests import HockeyGameFactory
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from organizations.tests import OrganizationFactory
from players.tests import HockeyPlayerFactory
from seasons.models import HockeySeasonRoster
from seasons.tests import HockeySeasonRosterFactory, SeasonFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class SeasonRosterCreateViewTests(BaseTestCase):
    url = 'teams:season_rosters:create'

    @classmethod
    def setUpTestData(cls):
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.mm_aa = DivisionFactory(name='Midget Minor AA', league=cls.liahl)
        cls.icecats = TeamFactory(name='Green Machine IceCats', division=cls.mm_aa)
        cls.liahl_season = SeasonFactory(league=cls.liahl)

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)

        self.hockey_sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='manager')
        self.hockey_manager = ManagerFactory(user=self.user, team=self.icecats)

        self.hockey_players = HockeyPlayerFactory.create_batch(5, sport=self.ice_hockey, team=self.icecats)
        self.formatted_url = self.format_url(team_pk=self.icecats.pk)
        self.login(user=self.user)

    # General
    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.formatted_url)
        self.assertRedirects(response, self.get_login_required_url(self.formatted_url))

    def test_sport_not_configured(self):
        team = TeamFactory()
        ManagerFactory(team=team, user=self.user)
        response = self.client.get(self.format_url(team_pk=team.pk), follow=True)
        self.assertTemplateUsed(response, 'sport_not_configured_msg.html')

    def test_has_permission_false(self):
        self.client.logout()
        user = UserFactory()
        SportRegistrationFactory(user=user, sport=self.ice_hockey, role='coach')
        CoachFactory(user=user, team__division__league__sport=self.ice_hockey)
        self.login(user=user)
        response = self.client.get(self.formatted_url)
        self.assert_404(response)

    def test_team_dne(self):
        response = self.client.get(self.format_url(team_pk=1000))
        self.assert_404(response)

    def test_form_kwargs(self):
        response = self.client.get(self.formatted_url)
        form = response.context['form']
        instance = form.instance

        self.assertEqual(form.team.pk, self.icecats.pk)
        self.assertEqual(instance.team.pk, self.icecats.pk)
        self.assertEqual(instance.created_by.pk, self.user.pk)

    # GET
    def test_get(self):
        response = self.client.get(self.formatted_url)
        context = response.context
        self.assert_200(response)
        self.assertTemplateUsed(response, 'seasons/season_roster_create.html')
        self.assertEqual(context['team'].pk, self.icecats.pk)
        self.assertEqual(context.get('team_display_name'), 'Green Machine IceCats - Midget Minor AA')
        self.assertIsNotNone(context.get('past_seasons'))
        self.assertEqual(context.get('active_tab'), 'season_rosters')

    # POST
    def test_post_valid_hockeyseasonroster(self):
        data = {
            'season': [self.liahl_season.pk],
            'players': [player.pk for player in self.hockey_players],
            'name': 'Main Squad'
        }

        response = self.client.post(self.formatted_url, data=data, follow=True)
        roster = HockeySeasonRoster.objects.first()

        self.assertHasMessage(response, 'Your season roster has been created.')
        url = reverse('teams:season_rosters:list', kwargs={'team_pk': self.icecats.pk})
        self.assertRedirects(response, url)
        self.assertEqual(roster.created_by.id, self.user.id)
        self.assertEqual(roster.team.id, self.icecats.id)

    def test_post_invalid_hockeyseasonroster(self):
        response = self.client.post(self.formatted_url, data={'season': [], 'players': []})
        self.assertFormError(response, 'form', 'players', 'This field is required.')
        self.assertFormError(response, 'form', 'season', 'This field is required.')
        self.assertTemplateUsed(response, 'seasons/season_roster_create.html')

    def test_post_default_season_roster_already_exists(self):
        # This tests to make sure you can't have more than 1 default season roster for a given team/season
        player_ids = [player.pk for player in self.hockey_players]
        HockeySeasonRosterFactory(season=self.liahl_season, team=self.icecats, players=player_ids, default=True)

        data = {'season': [self.liahl_season.pk], 'players': player_ids, 'default': True}
        response = self.client.post(self.formatted_url, data=data)
        self.assertFormError(response, 'form', 'default',
                             'A default season roster for this team and season already exists.')

    def test_post_duplicate_name_for_season_and_team(self):
        HockeySeasonRosterFactory(season=self.liahl_season, team=self.icecats, name='Main Squad')
        player_ids = [player.pk for player in self.hockey_players]
        data = {'season': [self.liahl_season.pk], 'players': player_ids, 'name': 'Main Squad'}
        response = self.client.post(self.formatted_url, data=data)
        self.assertFormError(response, 'form', 'name', 'Name must be unique for this team and season.')


class SeasonRosterUpdateViewTests(BaseTestCase):
    url = 'teams:season_rosters:update'

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)

        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)
        self.icecats = TeamFactory(name='Green Machine IceCats', division=self.mm_aa)
        self.past_season, self.current_season, _ = self.create_past_current_future_seasons(league=self.liahl)

        self.hockey_sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='manager')
        self.hockey_manager = ManagerFactory(user=self.user, team=self.icecats)

        self.hockey_players = HockeyPlayerFactory.create_batch(5, sport=self.ice_hockey, team=self.icecats)
        self.hockey_player_ids = [player.pk for player in self.hockey_players]
        self.season_roster = HockeySeasonRosterFactory(season=self.current_season, team=self.icecats,
                                                       players=self.hockey_player_ids, name='Bash Brothers',
                                                       created_by=self.user)
        self.formatted_url = self.format_url(pk=self.season_roster.pk, team_pk=self.icecats.pk)
        self.login(user=self.user)

    # General
    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.formatted_url)
        self.assertRedirects(response, self.get_login_required_url(self.formatted_url))

    def test_sport_not_configured(self):
        team = TeamFactory()
        ManagerFactory(team=team, user=self.user)
        response = self.client.get(self.format_url(team_pk=team.pk, pk=self.season_roster.pk), follow=True)
        self.assertTemplateUsed(response, 'sport_not_configured_msg.html')

    def test_has_permission_false_not_team_manager(self):
        self.client.logout()
        user = UserFactory()
        SportRegistrationFactory(user=user, sport=self.ice_hockey, role='coach')
        CoachFactory(user=user, team__division__league__sport=self.ice_hockey)
        ManagerFactory(user=user, team=TeamFactory(division=self.mm_aa))
        self.login(user=user)
        response = self.client.get(self.formatted_url)
        self.assert_404(response)

    def test_has_permission_false_inactive_team_manager(self):
        self.hockey_manager.is_active = False
        self.hockey_manager.save()
        response = self.client.get(self.formatted_url)
        self.assert_404(response)

    def test_team_dne(self):
        response = self.client.get(self.format_url(team_pk=1000, pk=self.season_roster.pk))
        self.assert_404(response)

    def test_form_kwargs(self):
        # Current season
        response = self.client.get(self.formatted_url)
        form = response.context['form']
        self.assertTrue(form.fields['season'].disabled)
        self.assertFalse(form.fields['name'].disabled)
        # Past season
        season_roster = HockeySeasonRosterFactory(team=self.icecats, season=self.past_season)
        response = self.client.get(self.format_url(team_pk=self.icecats.pk, pk=season_roster.pk))
        form = response.context['form']
        for k, v in form.fields.items():
            self.assertTrue(v.disabled)

    def test_season_roster_dne(self):
        response = self.client.get(self.format_url(team_pk=self.icecats.pk, pk=1000))
        self.assert_404(response)

    def test_get_object_qs_filtered_by_team(self):
        # This will create a hockey season roster with a random team that is different from self.icecats
        season_roster = HockeySeasonRosterFactory()
        response = self.client.get(self.format_url(team_pk=self.icecats.pk, pk=season_roster.pk))
        self.assert_404(response)

    # GET
    def test_get(self):
        response = self.client.get(self.formatted_url)
        context = response.context
        self.assert_200(response)
        self.assertTemplateUsed(response, 'seasons/season_roster_update.html')
        self.assertEqual(context['team'].pk, self.icecats.pk)
        self.assertEqual(context['form'].instance.pk, self.season_roster.pk)
        self.assertEqual(context.get('team_display_name'), 'Green Machine IceCats - Midget Minor AA')
        self.assertIsNotNone(context.get('past_seasons'))
        self.assertEqual(context.get('active_tab'), 'season_rosters')

    # POST
    def test_post_valid_changed_form(self):
        post_data = {
            'players': self.hockey_player_ids,
            'default': True,
            'name': 'Bash Brothers'
        }
        response = self.client.post(self.formatted_url, data=post_data, follow=True)
        self.assertTrue(HockeySeasonRoster.objects.first().default)
        self.assertHasMessage(response, 'Your season roster has been updated.')
        self.assertRedirects(response, reverse('teams:season_rosters:list', kwargs={'team_pk': self.icecats.pk}))

    def test_post_created_by_doesnt_change(self):
        user = UserFactory(password=self.password)
        SportRegistrationFactory(user=user, sport=self.ice_hockey, role='manager')
        ManagerFactory(user=user, team=self.icecats)
        self.client.logout()
        self.login(user=user)
        post_data = {
            'players': self.hockey_player_ids,
            'name': 'My Season Roster'
        }
        self.client.post(self.formatted_url, data=post_data)
        roster = HockeySeasonRoster.objects.first()
        # Make sure created_by doesn't get updated.
        self.assertEqual(roster.created_by.id, self.user.id)
        self.assertEqual(roster.name, 'My Season Roster')

    def test_post_unchanged_form(self):
        post_data = {
            'players': self.hockey_player_ids,
            'default': False,
            'name': 'Bash Brothers'
        }
        response = self.client.post(self.formatted_url, data=post_data, follow=True)
        self.assertNoMessage(response, 'Your season roster has been updated.')
        self.assertRedirects(response, reverse('teams:season_rosters:list', kwargs={'team_pk': self.icecats.pk}))

    def test_post_invalid_form(self):
        post_data = {
            'players': [],
            'default': False
        }
        response = self.client.post(self.formatted_url, data=post_data, follow=True)
        self.assertFormError(response, 'form', 'players', 'This field is required.')
        self.assertTemplateUsed(response, 'seasons/season_roster_update.html')

    def test_duplicate_season_roster_for_season_and_team(self):
        # This tests to make sure you can't have more than 1 default season roster for a given team/season
        HockeySeasonRosterFactory(season=self.current_season, team=self.icecats, players=self.hockey_player_ids,
                                  default=True)

        post_data = {'default': True}
        response = self.client.post(self.formatted_url, data=post_data)
        self.assertFormError(response, 'form', 'default',
                             'A default season roster for this team and season already exists.')

    def test_duplicate_name_for_season_and_team(self):
        HockeySeasonRosterFactory(season=self.current_season, team=self.icecats, players=self.hockey_player_ids,
                                  name='Main Squad')
        post_data = {'name': 'Main Squad'}
        response = self.client.post(self.formatted_url, data=post_data)
        self.assertFormError(response, 'form', 'name', 'Name must be unique for this team and season.')


class LeagueSeasonDetailViewTestCase(BaseTestCase):
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
        self.icecats_mm_aa = TeamFactory(name='Green Machine IceCats', division=self.mm_aa,
                                         organization=self.icecats_organization)
        self.icecats_peewee = TeamFactory(name='Green Machine IceCats', division=self.peewee,
                                          organization=self.icecats_organization)
        self.managers = [ManagerFactory(user=self.user, team=self.icecats_mm_aa)]
        self.edge_mm_aa = TeamFactory(name='Long Island Edge', division=self.mm_aa,
                                      organization=self.edge_organization)
        self.edge_peewee = TeamFactory(name='Long Island Edge', division=self.peewee,
                                       organization=self.edge_organization)

        self.rebels_mm_aa = TeamFactory(name='Long Island Rebels', division=self.mm_aa,
                                        organization=self.rebels_organization)
        self.rebels_peewee = TeamFactory(name='Long Island Rebels', division=self.peewee,
                                         organization=self.rebels_organization)
        self.bruins = TeamFactory(name='Boston Bruins', division=self.atlantic, organization=self.bruins_organization)
        self.sabres = TeamFactory(name='Buffalo Sabres', division=self.atlantic, organization=self.sabres_organization)

        self.teams = [self.icecats_mm_aa, self.icecats_peewee, self.edge_mm_aa, self.edge_peewee, self.rebels_mm_aa,
                      self.rebels_peewee]


class AbstractScheduleViewTestCase(LeagueSeasonDetailViewTestCase):
    """
    Abstract test case that sets up all of the necessary objects to test a schedule view
    """

    def _create_game(self, home_team, away_team, season):
        return HockeyGameFactory(home_team=home_team, away_team=away_team, team=home_team, season=season,
                                 type=self.game_type, point_value=self.point_value)

    def setUp(self):
        super().setUp()

        self.start_date = date.today()
        self.past_start_date = self.start_date - timedelta(days=365)
        self.future_start_date = self.start_date + timedelta(days=365)
        self.previous_season = SeasonFactory(league=self.liahl, start_date=self.past_start_date,
                                             end_date=self.start_date - timedelta(days=2),
                                             teams=self.teams)
        self.current_season = SeasonFactory(league=self.liahl, start_date=self.start_date,
                                            end_date=self.future_start_date, teams=self.teams)
        self.next_season = SeasonFactory(league=self.liahl, start_date=self.future_start_date,
                                         end_date=self.future_start_date + timedelta(days=365), teams=self.teams)

        self.game_type = GenericChoiceFactory(short_value='exhibition', long_value='Exhibition', type='game_type',
                                              content_object=self.ice_hockey)
        self.point_value = GenericChoiceFactory(short_value='2', long_value='2', type='game_point_value',
                                                content_object=self.ice_hockey)
        self.game1 = self._create_game(self.icecats_mm_aa, self.edge_mm_aa, self.current_season)
        self.game2 = self._create_game(self.icecats_mm_aa, self.rebels_mm_aa, self.current_season)
        self.game3 = self._create_game(self.icecats_peewee, self.edge_peewee, self.current_season)
        self._create_game(self.icecats_peewee, self.rebels_peewee, self.previous_season)
        # Game for another league (should be excluded)
        self.nhl_season = SeasonFactory(league=self.nhl)
        self._create_game(self.bruins, self.sabres, self.nhl_season)
        self.games = [self.game1, self.game2, self.game3]
        self.login(user=self.user)


class SeasonDetailScheduleViewTests(AbstractScheduleViewTestCase):
    url = 'leagues:seasons:schedule'

    def setUp(self):
        super().setUp()
        self.formatted_url = self.format_url(slug=self.liahl.slug, season_pk=self.current_season.pk)

    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.formatted_url)

    def test_league_dne(self):
        response = self.client.get(self.format_url(slug='dne', season_pk=1))
        self.assert_404(response)

    def test_season_pk_for_different_league(self):
        response = self.client.get(self.format_url(slug=self.liahl.slug, season_pk=self.nhl_season.pk))
        self.assert_404(response)

    def test_sport_not_configured(self):
        sport = SportFactory()
        league = LeagueFactory(sport=sport)
        season = SeasonFactory(league=league)
        self.assertSportNotConfigured(self.format_url(slug=league.slug, season_pk=season.pk))

    # GET
    def test_get(self):
        response = self.client.get(self.formatted_url)
        team_ids_managed_by_user = [m.team_id for m in self.managers]
        context = response.context
        self.assert_200(response)
        self.assertTemplateUsed(response, 'seasons/season_detail_schedule.html')
        self.assertEqual(context.get('league'), self.liahl)
        self.assertEqual(context.get('season'), self.current_season)
        self.assertIsNotNone(context.get('past_seasons'))
        self.assertEqual(context.get('sport'), self.ice_hockey)
        self.assertEqual(context.get('active_tab'), 'schedule')
        self.assertListEqual(list(context.get('team_ids_managed_by_user')), team_ids_managed_by_user)
        self.assertFalse(context.get('is_scorekeeper'))
        self.assertListEqual(list(context.get('games')), self.games)
        self.assertTrue(context.get('has_games'))
        self.assertEqual(context.get('current_season_page_url'),
                         reverse('leagues:schedule', kwargs={'slug': self.liahl.slug}))


class SeasonDetailDivisionsViewTests(LeagueSeasonDetailViewTestCase):
    url = 'leagues:seasons:divisions'

    def setUp(self):
        super().setUp()
        self.start_date = date.today()
        self.future_start_date = self.start_date + timedelta(days=365)
        self.current_season = SeasonFactory(league=self.liahl, start_date=self.start_date,
                                            end_date=self.future_start_date, teams=self.teams)
        self.login(user=self.user)
        self.formatted_url = self.format_url(slug=self.liahl.slug, season_pk=self.current_season.pk)

    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.formatted_url)

    def test_league_dne(self):
        response = self.client.get(self.format_url(slug='dne', season_pk=1))
        self.assert_404(response)

    def test_season_pk_for_different_league(self):
        season = SeasonFactory()
        response = self.client.get(self.format_url(slug=self.liahl.slug, season_pk=season.pk))
        self.assert_404(response)

    def test_get(self):
        response = self.client.get(self.formatted_url)
        context = response.context
        self.assert_200(response)
        self.assertTemplateUsed('seasons/season_detail_divisions.html')
        self.assertEqual(context.get('league'), self.liahl)
        self.assertEqual(context.get('active_tab'), 'divisions')
        self.assertIsNotNone(context.get('past_seasons'))
        expected = [
            [self.mm_aa, self.peewee],
        ]
        self.assertListEqual(list(context.get('chunked_divisions')), expected)
        self.assertEqual(context.get('current_season_page_url'),
                         reverse('leagues:divisions', kwargs={'slug': self.liahl.slug}))
