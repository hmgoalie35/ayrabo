from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from coaches.tests import CoachFactory
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from players.tests import HockeyPlayerFactory
from seasons.models import HockeySeasonRoster
from seasons.tests import SeasonFactory, HockeySeasonRosterFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class SeasonRosterCreateViewTests(BaseTestCase):
    url = 'teams:season_rosters:create'

    @classmethod
    def setUpTestData(cls):
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.liahl = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.mm_aa = DivisionFactory(name='Midget Minor AA', league=cls.liahl)
        cls.icecats = TeamFactory(name='Green Machine Icecats', division=cls.mm_aa)
        cls.liahl_season = SeasonFactory(league=cls.liahl)

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)

        self.hockey_sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True, roles_mask=0)
        self.hockey_sr.set_roles(['Manager'])
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
        sr = SportRegistrationFactory(user=user, sport=self.ice_hockey)
        sr.set_roles(['Coach'])
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
        self.assertEqual(context['team'].pk, self.icecats.pk)
        self.assert_200(response)
        self.assertTemplateUsed(response, 'seasons/season_roster_create.html')

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
        self.assertRedirects(response, self.hockey_sr.get_absolute_url())
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


class SeasonRosterListViewTests(BaseTestCase):
    url = 'teams:season_rosters:list'

    @classmethod
    def setUpTestData(cls):
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.liahl = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.mm_aa = DivisionFactory(name='Midget Minor AA', league=cls.liahl)
        cls.icecats = TeamFactory(name='Green Machine Icecats', division=cls.mm_aa)
        cls.liahl_season = SeasonFactory(league=cls.liahl)

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)

        self.hockey_sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True, roles_mask=0)
        self.hockey_sr.set_roles(['Manager'])
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

    def test_has_permission_false_not_manager(self):
        team = TeamFactory(division=self.mm_aa)
        response = self.client.get(self.format_url(team_pk=team.pk))
        self.assert_404(response)

    def test_has_permission_false_inactive_manager(self):
        self.hockey_manager.is_active = False
        self.hockey_manager.save()
        response = self.client.get(self.formatted_url)
        self.assert_404(response)

    def test_team_dne(self):
        response = self.client.get(self.format_url(team_pk=1000))
        self.assert_404(response)

    # GET
    def test_get(self):
        response = self.client.get(self.formatted_url)
        self.assert_200(response)
        self.assertTemplateUsed(response, 'seasons/season_roster_list.html')

    def test_get_context_populated(self):
        season_rosters = HockeySeasonRosterFactory.create_batch(5, season=self.liahl_season, team=self.icecats)
        players = HockeyPlayerFactory.create_batch(4)
        players[0].is_active = False
        players[0].save()
        season_rosters[0].players.set(players)
        response = self.client.get(self.formatted_url)
        context = response.context
        self.assertEqual(context['team'].pk, self.icecats.pk)
        self.assertEqual(set(context['season_rosters']), set(season_rosters))
        self.assertEqual(context['season_rosters'][season_rosters[0]].count(), 3)


class SeasonRosterUpdateViewTests(BaseTestCase):
    url = 'teams:season_rosters:update'

    @classmethod
    def setUpTestData(cls):
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.liahl = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.mm_aa = DivisionFactory(name='Midget Minor AA', league=cls.liahl)
        cls.icecats = TeamFactory(name='Green Machine Icecats', division=cls.mm_aa)
        cls.liahl_season = SeasonFactory(league=cls.liahl)

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)

        self.hockey_sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True, roles_mask=0)
        self.hockey_sr.set_roles(['Manager'])
        self.hockey_manager = ManagerFactory(user=self.user, team=self.icecats)

        self.hockey_players = HockeyPlayerFactory.create_batch(5, sport=self.ice_hockey, team=self.icecats)
        self.hockey_player_ids = [player.pk for player in self.hockey_players]
        self.season_roster = HockeySeasonRosterFactory(season=self.liahl_season, team=self.icecats,
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
        sr = SportRegistrationFactory(user=user, sport=self.ice_hockey)
        sr.set_roles(['Coach'])
        CoachFactory(user=user, team__division__league__sport=self.ice_hockey)
        self.login(user=user)
        response = self.client.get(self.formatted_url)
        self.assert_404(response)

    def test_has_permission_false_inactive_team_manager(self):
        self.hockey_manager.is_active = False
        self.hockey_manager.save()
        response = self.client.get(self.formatted_url)
        self.assert_404(response)

    def test_has_permission_false_season_roster_is_for_different_team(self):
        # This will create a hockey season roster with a random team that is different from self.icecats
        season_roster = HockeySeasonRosterFactory()
        response = self.client.get(self.format_url(team_pk=self.icecats.pk, pk=season_roster.pk))
        self.assert_404(response)

    def test_team_dne(self):
        response = self.client.get(self.format_url(team_pk=1000, pk=self.season_roster.pk))
        self.assert_404(response)

    def test_form_kwargs(self):
        response = self.client.get(self.formatted_url)
        form = response.context['form']
        self.assertTrue(form.fields['season'].disabled)

    def test_season_roster_dne(self):
        response = self.client.get(self.format_url(team_pk=self.icecats.pk, pk=1000))
        self.assert_404(response)

    # GET
    def test_get(self):
        response = self.client.get(self.formatted_url)
        context = response.context
        self.assert_200(response)
        self.assertTemplateUsed(response, 'seasons/season_roster_update.html')
        self.assertEqual(context['team'].pk, self.icecats.pk)
        self.assertEqual(context['form'].instance.pk, self.season_roster.pk)

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
        hockey_sr = SportRegistrationFactory(user=user, sport=self.ice_hockey, roles_mask=0)
        hockey_sr.set_roles(['Manager'])
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
        HockeySeasonRosterFactory(season=self.liahl_season, team=self.icecats, players=self.hockey_player_ids,
                                  default=True)

        post_data = {'default': True}
        response = self.client.post(self.formatted_url, data=post_data)
        self.assertFormError(response, 'form', 'default',
                             'A default season roster for this team and season already exists.')

    def test_duplicate_name_for_season_and_team(self):
        HockeySeasonRosterFactory(season=self.liahl_season, team=self.icecats, players=self.hockey_player_ids,
                                  name='Main Squad')
        post_data = {'name': 'Main Squad'}
        response = self.client.post(self.formatted_url, data=post_data)
        self.assertFormError(response, 'form', 'name', 'Name must be unique for this team and season.')
