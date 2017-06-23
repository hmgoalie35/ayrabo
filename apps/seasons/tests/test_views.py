from django.core import mail
from django.urls import reverse

from accounts.tests import UserFactory
from divisions.tests import DivisionFactory
from escoresheet.utils.testing_utils import BaseTestCase
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from players.tests import HockeyPlayerFactory
from seasons.models import HockeySeasonRoster
from seasons.tests import SeasonFactory, HockeySeasonRosterFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


class SeasonRosterCreateViewTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.liahl = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.mm_aa = DivisionFactory(name='Midget Minor AA', league=cls.liahl)
        cls.icecats = TeamFactory(name='Green Machine Icecats', division=cls.mm_aa)
        cls.liahl_season = SeasonFactory(league=cls.liahl)

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)

        self.hockey_sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True, roles_mask=0)
        self.hockey_sr.set_roles(['Manager'])
        self.hockey_manager = ManagerFactory(user=self.user, team=self.icecats)

        self.hockey_players = HockeyPlayerFactory.create_batch(5, sport=self.ice_hockey, team=self.icecats)
        self.url = reverse('teams:season_rosters:create', kwargs={'team_pk': self.icecats.pk})
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous(self):
        self.client.logout()
        response = self.client.get(self.url)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'seasons/season_roster_create.html')

    def test_get_redirects_if_no_manager_role(self):
        self.hockey_sr.set_roles(['Player', 'Coach'])
        # self.baseball_sr.set_roles(['Referee'])
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertHasMessage(response, 'You do not have permission to perform this action.')

    def test_get_invalid_team_pk(self):
        response = self.client.get(reverse('teams:season_rosters:create', kwargs={'team_pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_get_user_not_team_manager(self):
        team = TeamFactory(division=self.mm_aa)
        response = self.client.get(reverse('teams:season_rosters:create', kwargs={'team_pk': team.pk}))
        self.assertEqual(response.status_code, 404)

    def test_get_sport_not_configured(self):
        team = TeamFactory()
        ManagerFactory(team=team, user=self.user)
        response = self.client.get(reverse('teams:season_rosters:create', kwargs={'team_pk': team.pk}), follow=True)
        self.assertTemplateUsed(response, 'sport_not_configured_msg.html')
        msg = "{sport} hasn't been configured correctly in our system. " \
              "If you believe this is an error please contact us.".format(sport=team.division.league.sport.name)
        self.assertEqual(response.context['message'], msg)
        self.assertEqual(len(mail.outbox), 1)

    def test_get_context_populated(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(context['team'].pk, self.icecats.pk)
        form = context['form']
        # Make sure team field is disabled
        self.assertTrue(form.fields['team'].disabled)
        # Make sure initial team is populated
        self.assertDictEqual(form.initial, {'team': self.icecats.pk})

    def test_form_season_team_players_querysets(self):
        """
        This is testing the form excludes seasons, teams and players that are in a different league than icecats
        """
        # This object will have a different league than self.icecats
        season = SeasonFactory()
        team = TeamFactory()
        player = HockeyPlayerFactory(sport=self.ice_hockey, team=team)
        response = self.client.get(
                reverse('teams:season_rosters:create', kwargs={'team_pk': self.icecats.pk}))

        form = response.context['form']
        self.assertNotIn(season, form.fields['season'].queryset)
        self.assertNotIn(team, form.fields['team'].queryset)
        self.assertNotIn(player, form.fields['players'].queryset)

    def test_form_players_qs_are_of_same_team(self):
        li_edge = TeamFactory(name='Long Island Edge', division=self.mm_aa)
        # Players in same league and division but different teams should not be available for selection in the form.
        HockeyPlayerFactory.create_batch(5, sport=self.ice_hockey, team=li_edge)
        response = self.client.get(self.url)
        form = response.context['form']
        form_players = list(form.fields['players'].queryset)
        form_players = sorted(form_players, key=lambda obj: obj.pk)
        self.assertListEqual(list(form_players), sorted(self.hockey_players, key=lambda obj: obj.pk))

    # POST
    def test_post_redirects_if_no_manager_role(self):
        self.hockey_sr.set_roles(['Player', 'Coach'])
        # self.baseball_sr.set_roles(['Referee'])
        response = self.client.post(self.url, data={}, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertHasMessage(response, 'You do not have permission to perform this action.')

    def test_post_sport_not_configured(self):
        team = TeamFactory()
        ManagerFactory(team=team, user=self.user)
        response = self.client.post(reverse('teams:season_rosters:create', kwargs={'team_pk': team.pk}), data={},
                                    follow=True)
        self.assertTemplateUsed(response, 'sport_not_configured_msg.html')
        msg = "{sport} hasn't been configured correctly in our system. " \
              "If you believe this is an error please contact us.".format(sport=team.division.league.sport.name)
        self.assertEqual(response.context['message'], msg)
        self.assertEqual(len(mail.outbox), 1)

    def test_post_invalid_team_pk(self):
        response = self.client.post(reverse('teams:season_rosters:create', kwargs={'team_pk': 1000}), data={},
                                    follow=True)
        self.assertEqual(response.status_code, 404)

    def test_post_user_not_team_manager(self):
        team = TeamFactory(division=self.mm_aa)
        response = self.client.post(reverse('teams:season_rosters:create', kwargs={'team_pk': team.pk}), data={},
                                    follow=True)
        self.assertEqual(response.status_code, 404)

    # This is only testing hockey season rosters
    # TODO add in tests for other sports as they become available
    def test_post_valid_hockeyseasonroster_form_data(self):
        post_data = {'season': [self.liahl_season.pk], 'players': [player.pk for player in self.hockey_players]}
        response = self.client.post(
                reverse('teams:season_rosters:create', kwargs={'team_pk': self.icecats.pk}),
                data=post_data,
                follow=True)
        self.assertHasMessage(response, 'Season roster created for {team}.'.format(team=self.icecats))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(HockeySeasonRoster.objects.count(), 1)

    def test_post_invalid_hockeyseasonroster_form_data(self):
        response = self.client.post(
                reverse('teams:season_rosters:create', kwargs={'team_pk': self.icecats.pk}),
                data={'season': None, 'players': []})
        self.assertFormError(response, 'form', 'players', 'This field is required.')

    def test_duplicate_season_roster_for_season_and_team(self):
        # This tests to make sure you can't have more than 1 default season roster for a given team/season
        player_ids = [player.pk for player in self.hockey_players]
        HockeySeasonRosterFactory(season=self.liahl_season, team=self.icecats, players=player_ids, default=True)

        post_data = {'season': [self.liahl_season.pk], 'players': player_ids, 'default': True}
        response = self.client.post(reverse('teams:season_rosters:create', kwargs={'team_pk': self.icecats.pk}),
                                    data=post_data)
        self.assertFormError(response, 'form', 'default',
                             'A default season roster for this team and season already exists.')


class SeasonRosterListViewTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.liahl = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.mm_aa = DivisionFactory(name='Midget Minor AA', league=cls.liahl)
        cls.icecats = TeamFactory(name='Green Machine Icecats', division=cls.mm_aa)
        cls.liahl_season = SeasonFactory(league=cls.liahl)

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)

        self.hockey_sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True, roles_mask=0)
        self.hockey_sr.set_roles(['Manager'])
        self.hockey_manager = ManagerFactory(user=self.user, team=self.icecats)

        self.hockey_players = HockeyPlayerFactory.create_batch(5, sport=self.ice_hockey, team=self.icecats)
        self.url = reverse('teams:season_rosters:list', kwargs={'team_pk': self.icecats.pk})
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous(self):
        self.client.logout()
        response = self.client.get(self.url)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'seasons/season_roster_list.html')

    def test_get_redirects_if_no_manager_role(self):
        self.hockey_sr.set_roles(['Player', 'Coach'])
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertHasMessage(response, 'You do not have permission to perform this action.')

    def test_get_sport_not_configured(self):
        team = TeamFactory()
        ManagerFactory(team=team, user=self.user)
        response = self.client.get(reverse('teams:season_rosters:list', kwargs={'team_pk': team.pk}), follow=True)
        self.assertTemplateUsed(response, 'sport_not_configured_msg.html')
        msg = "{sport} hasn't been configured correctly in our system. " \
              "If you believe this is an error please contact us.".format(sport=team.division.league.sport.name)
        self.assertEqual(response.context['message'], msg)
        self.assertEqual(len(mail.outbox), 1)

    def test_get_invalid_team_pk(self):
        response = self.client.get(reverse('teams:season_rosters:list', kwargs={'team_pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_get_user_not_team_manager(self):
        team = TeamFactory(division=self.mm_aa)
        response = self.client.get(reverse('teams:season_rosters:list', kwargs={'team_pk': team.pk}))
        self.assertEqual(response.status_code, 404)

    def test_get_inactive_manager(self):
        self.hockey_manager.is_active = False
        self.hockey_manager.save()
        response = self.client.get(reverse('teams:season_rosters:list', kwargs={'team_pk': self.icecats.pk}))
        self.assertEqual(response.status_code, 404)

    def test_get_context_populated(self):
        season_rosters = HockeySeasonRosterFactory.create_batch(5, season=self.liahl_season, team=self.icecats)
        players = HockeyPlayerFactory.create_batch(4)
        players[0].is_active = False
        players[0].save()
        season_rosters[0].players.set(players)
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(context['team'].pk, self.icecats.pk)

        self.assertEqual(set(context['season_rosters']), set(season_rosters))

        self.assertEqual(context['season_rosters'][season_rosters[0]].count(), 3)


class SeasonRosterUpdateViewTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.liahl = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.mm_aa = DivisionFactory(name='Midget Minor AA', league=cls.liahl)
        cls.icecats = TeamFactory(name='Green Machine Icecats', division=cls.mm_aa)
        cls.liahl_season = SeasonFactory(league=cls.liahl)

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)

        self.hockey_sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True, roles_mask=0)
        self.hockey_sr.set_roles(['Manager'])
        self.hockey_manager = ManagerFactory(user=self.user, team=self.icecats)

        self.hockey_players = HockeyPlayerFactory.create_batch(5, sport=self.ice_hockey, team=self.icecats)
        self.hockey_player_ids = [player.pk for player in self.hockey_players]
        self.season_roster = HockeySeasonRosterFactory(season=self.liahl_season, team=self.icecats,
                                                       players=self.hockey_player_ids)
        self.url = self.season_roster.get_absolute_url()
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous(self):
        self.client.logout()
        response = self.client.get(self.url)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'seasons/season_roster_update.html')

    def test_get_redirects_if_no_manager_role(self):
        self.hockey_sr.set_roles(['Player', 'Coach'])
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertHasMessage(response, 'You do not have permission to perform this action.')

    def test_get_sport_not_configured(self):
        team = TeamFactory()
        ManagerFactory(team=team, user=self.user)
        response = self.client.get(
                reverse('teams:season_rosters:update', kwargs={'team_pk': team.pk, 'pk': self.season_roster.pk}),
                follow=True)
        self.assertTemplateUsed(response, 'sport_not_configured_msg.html')
        msg = "{sport} hasn't been configured correctly in our system. " \
              "If you believe this is an error please contact us.".format(sport=team.division.league.sport.name)
        self.assertEqual(response.context['message'], msg)
        self.assertEqual(len(mail.outbox), 1)

    def test_get_invalid_team_pk(self):
        response = self.client.get(
                reverse('teams:season_rosters:update', kwargs={'team_pk': 1000, 'pk': self.season_roster.pk}))
        self.assertEqual(response.status_code, 404)

    def test_get_user_not_team_manager(self):
        team = TeamFactory(division=self.mm_aa)
        response = self.client.get(
                reverse('teams:season_rosters:update', kwargs={'team_pk': team.pk, 'pk': self.season_roster.pk}))
        self.assertEqual(response.status_code, 404)

    def test_get_inactive_manager(self):
        self.hockey_manager.is_active = False
        self.hockey_manager.save()
        response = self.client.get(
                reverse('teams:season_rosters:update',
                        kwargs={'team_pk': self.icecats.pk, 'pk': self.season_roster.pk}))
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_season_roster_pk(self):
        response = self.client.get(
                reverse('teams:season_rosters:update', kwargs={'team_pk': self.icecats.pk, 'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_get_season_roster_is_for_different_team(self):
        # This will create a hockey season roster with a random team that is different from self.icecats
        season_roster = HockeySeasonRosterFactory()
        response = self.client.get(
                reverse('teams:season_rosters:update', kwargs={'team_pk': self.icecats.pk, 'pk': season_roster.pk}))
        self.assertEqual(response.status_code, 404)

    def test_get_context_populated(self):
        # Create some extra hockey players to make sure the form is only showing players of desired team
        HockeyPlayerFactory.create_batch(5)
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(context['team'].pk, self.icecats.pk)
        self.assertIsNotNone(context['form'])
        self.assertEqual(context['form'].instance.pk, self.season_roster.pk)
        qs = context['form'].fields['players'].queryset
        players = sorted(list(qs), key=lambda obj: obj.pk)
        self.assertListEqual(players, sorted(self.hockey_players, key=lambda obj: obj.pk))

    # POST
    def test_post_sport_not_configured(self):
        team = TeamFactory()
        ManagerFactory(team=team, user=self.user)
        response = self.client.post(
                reverse('teams:season_rosters:update', kwargs={'team_pk': team.pk, 'pk': self.season_roster.pk}),
                data={},
                follow=True)
        self.assertTemplateUsed(response, 'sport_not_configured_msg.html')
        msg = "{sport} hasn't been configured correctly in our system. " \
              "If you believe this is an error please contact us.".format(sport=team.division.league.sport.name)
        self.assertEqual(response.context['message'], msg)
        self.assertEqual(len(mail.outbox), 1)

    def test_post_valid_changed_form(self):
        post_data = {
            'players': self.hockey_player_ids,
            'default': True
        }
        response = self.client.post(self.url, data=post_data, follow=True)
        self.assertTrue(HockeySeasonRoster.objects.first().default)
        self.assertHasMessage(response, 'Season roster for {team} successfully updated.'.format(team=self.icecats))
        self.assertRedirects(response, reverse('teams:season_rosters:list', kwargs={'team_pk': self.icecats.pk}))

    def test_post_valid_unchanged_form(self):
        post_data = {
            'players': self.hockey_player_ids,
            'default': False
        }
        response = self.client.post(self.url, data=post_data, follow=True)
        self.assertNoMessage(response, 'Season roster for {team} successfully updated.'.format(team=self.icecats))
        self.assertRedirects(response, reverse('teams:season_rosters:list', kwargs={'team_pk': self.icecats.pk}))

    def test_post_invalid_form(self):
        post_data = {
            'players': [],
            'default': False
        }
        response = self.client.post(self.url, data=post_data, follow=True)
        self.assertFormError(response, 'form', 'players', 'This field is required.')
        self.assertTemplateUsed(response, 'seasons/season_roster_update.html')

    def test_duplicate_season_roster_for_season_and_team(self):
        # This tests to make sure you can't have more than 1 default season roster for a given team/season
        HockeySeasonRosterFactory(season=self.liahl_season, team=self.icecats, players=self.hockey_player_ids,
                                  default=True)

        post_data = {'default': True}
        response = self.client.post(self.url, data=post_data)
        self.assertFormError(response, 'form', 'default',
                             'A default season roster for this team and season already exists.')
