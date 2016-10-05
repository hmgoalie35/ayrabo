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
        cls.baseball = SportFactory(name='Baseball')
        cls.mlb = LeagueFactory(full_name='Major League Baseball', sport=cls.baseball)
        cls.ale = DivisionFactory(name='American League East', league=cls.mlb)
        cls.yankees = TeamFactory(name='New York Yankees', division=cls.ale)
        cls.liahl_season = SeasonFactory(league=cls.liahl)

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)

        self.hockey_sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True, roles_mask=0)
        self.hockey_sr.set_roles(['Manager'])
        self.hockey_manager = ManagerFactory(user=self.user, team=self.icecats)

        self.baseball_sr = SportRegistrationFactory(user=self.user, sport=self.baseball, is_complete=True, roles_mask=0)
        self.baseball_sr.set_roles(['Manager'])
        self.baseball_manager = ManagerFactory(user=self.user, team=self.yankees)

        self.url = reverse('season:create_season_roster')
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous(self):
        self.client.logout()
        url = reverse('season:create_season_roster')
        response = self.client.get(url)
        result_url = '%s?next=%s' % (reverse('account_login'), url)
        self.assertRedirects(response, result_url)

    def test_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'seasons/create_season_roster.html')

    def test_get_redirects_if_no_manager_role(self):
        self.hockey_sr.set_roles(['Player', 'Coach'])
        self.baseball_sr.set_roles(['Referee'])
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertIn('You do not have permission to perform this action.', get_messages(response))

    # GET no team_pk in url
    def test_get_no_team_pk_in_url(self):
        response = self.client.get(self.url)
        self.assertIsNone(response.context['team'])
        expected = {
            'Ice Hockey': self.icecats,
            'Baseball': self.yankees
        }
        self.assertDictEqual(response.context['sport_team_mappings'], expected)

    # GET team_pk in url
    def test_get_user_not_teams_manager(self):
        team = TeamFactory(name='Fake Team')
        response = self.client.get(reverse('season:create_season_roster_team_param', kwargs={'team_pk': team.pk}))
        self.assertEqual(response.status_code, 404)

    def test_get_team_pk_in_url(self):
        response = self.client.get(
                reverse('season:create_season_roster_team_param', kwargs={'team_pk': self.icecats.pk}))

        self.assertEqual(response.context['team'].pk, self.icecats.pk)
        form = response.context['form']
        self.assertDictEqual(form.initial, {'team': self.icecats.pk})
        self.assertTrue(form.fields['team'].disabled)

    # This is only testing hockey season rosters
    # TODO add in tests for other sports as they become available
    def test_post_valid_hockeyseasonroster_form_data(self):
        hockey_players = HockeyPlayerFactory.create_batch(5, sport=self.ice_hockey, team=self.icecats)
        post_data = {'season': [self.liahl_season.pk], 'players': [player.pk for player in hockey_players]}
        response = self.client.post(
                reverse('season:create_season_roster_team_param', kwargs={'team_pk': self.icecats.pk}),
                data=post_data,
                follow=True)
        self.assertIn('Season roster created for {team}'.format(team=self.icecats), get_messages(response))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(HockeySeasonRoster.objects.count(), 1)

    def test_post_invalid_hockeyseasonroster_form_data(self):
        response = self.client.post(
                reverse('season:create_season_roster_team_param', kwargs={'team_pk': self.icecats.pk}),
                data={'season': None, 'players': []})
        self.assertFormError(response, 'form', 'players', 'This field is required.')

    def test_season_team_player_querysets_include_objects_of_same_league(self):
        # This object will have a different league than self.icecats
        season = SeasonFactory()
        team = TeamFactory()
        player = HockeyPlayerFactory(sport=self.ice_hockey, team=team)
        response = self.client.get(
                reverse('season:create_season_roster_team_param', kwargs={'team_pk': self.icecats.pk}))

        form = response.context['form']
        self.assertNotIn(season, form.fields['season'].queryset)
        self.assertNotIn(team, form.fields['team'].queryset)
        self.assertNotIn(player, form.fields['players'].queryset)
