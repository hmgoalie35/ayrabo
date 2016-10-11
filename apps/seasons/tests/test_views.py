from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.tests import UserFactory
from divisions.tests import DivisionFactory
from escoresheet.testing_utils import get_messages
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from players.tests import HockeyPlayerFactory
from seasons.models import HockeySeasonRoster
from seasons.tests import SeasonFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


class CreateSeasonRosterViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(CreateSeasonRosterViewTests, cls).setUpClass()
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
        self.url = reverse('team:create_season_roster', kwargs={'team_pk': self.icecats.pk})
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous(self):
        self.client.logout()
        response = self.client.get(self.url)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'seasons/create_season_roster.html')

    def test_get_redirects_if_no_manager_role(self):
        self.hockey_sr.set_roles(['Player', 'Coach'])
        # self.baseball_sr.set_roles(['Referee'])
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertIn('You do not have permission to perform this action.', get_messages(response))

    def test_get_invalid_team_pk(self):
        response = self.client.get(reverse('team:create_season_roster', kwargs={'team_pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_get_user_not_team_manager(self):
        team = TeamFactory(division=self.mm_aa)
        response = self.client.get(reverse('team:create_season_roster', kwargs={'team_pk': team.pk}))
        self.assertEqual(response.status_code, 404)

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
                reverse('team:create_season_roster', kwargs={'team_pk': self.icecats.pk}))

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
        form_player_qs = form.fields['players'].queryset
        self.assertListEqual(list(form_player_qs), self.hockey_players)

    # POST
    def test_post_redirects_if_no_manager_role(self):
        self.hockey_sr.set_roles(['Player', 'Coach'])
        # self.baseball_sr.set_roles(['Referee'])
        response = self.client.post(self.url, data={}, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertIn('You do not have permission to perform this action.', get_messages(response))

    def test_post_invalid_team_pk(self):
        response = self.client.post(reverse('team:create_season_roster', kwargs={'team_pk': 1000}), data={},
                                    follow=True)
        self.assertEqual(response.status_code, 404)

    def test_post_user_not_team_manager(self):
        team = TeamFactory(division=self.mm_aa)
        response = self.client.post(reverse('team:create_season_roster', kwargs={'team_pk': team.pk}), data={},
                                    follow=True)
        self.assertEqual(response.status_code, 404)

    # This is only testing hockey season rosters
    # TODO add in tests for other sports as they become available
    def test_post_valid_hockeyseasonroster_form_data(self):
        post_data = {'season': [self.liahl_season.pk], 'players': [player.pk for player in self.hockey_players]}
        response = self.client.post(
                reverse('team:create_season_roster', kwargs={'team_pk': self.icecats.pk}),
                data=post_data,
                follow=True)
        self.assertIn('Season roster created for {team}'.format(team=self.icecats), get_messages(response))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(HockeySeasonRoster.objects.count(), 1)

    def test_post_invalid_hockeyseasonroster_form_data(self):
        response = self.client.post(
                reverse('team:create_season_roster', kwargs={'team_pk': self.icecats.pk}),
                data={'season': None, 'players': []})
        self.assertFormError(response, 'form', 'players', 'This field is required.')
