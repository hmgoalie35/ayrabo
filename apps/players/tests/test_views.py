from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from players.tests import BaseballPlayerFactory, HockeyPlayerFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class PlayerUpdateViewTests(BaseTestCase):
    def _format_url(self, **kwargs):
        return reverse(self.url, kwargs=kwargs)

    @classmethod
    def setUpTestData(cls):
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.url = 'sportregistrations:players:update'
        cls.email = 'user@ayrabo.com'
        cls.password = 'myweakpassword'
        cls.user = UserFactory(email=cls.email, password=cls.password)
        cls.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.division = DivisionFactory(name='Midget Minor AA', league=cls.league)
        cls.team = TeamFactory(name='Green Machine IceCats', division=cls.division)

        cls.baseball_league = LeagueFactory(full_name='Major League Baseball', sport=cls.baseball)
        cls.baseball_division = DivisionFactory(name='American League East', league=cls.baseball_league)
        cls.baseball_team = TeamFactory(name='New York Yankees', division=cls.baseball_division)
        cls.baseball_player = BaseballPlayerFactory(user=cls.user, sport=cls.baseball, team=cls.baseball_team,
                                                    jersey_number=25)

        cls.sr = SportRegistrationFactory(user=cls.user, sport=cls.ice_hockey, is_complete=True)
        cls.sr_2 = SportRegistrationFactory(user=cls.user, sport=cls.baseball, is_complete=True)
        cls.sr.set_roles(['Player'])
        cls.sr_2.set_roles(['Player'])

    def setUp(self):
        self.post_data = {
            'jersey_number': 23,
            'position': 'LW',
            'handedness': 'Left'
        }
        self.player = HockeyPlayerFactory(user=self.user, sport=self.ice_hockey, team=self.team, **self.post_data)
        self.hockeyplayer_url = self._format_url(pk=self.sr.pk, player_pk=self.player.pk)
        self.baseballplayer_url = self._format_url(pk=self.sr_2.pk, player_pk=self.player.pk)

        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous(self):
        self.client.logout()
        response = self.client.get(self.hockeyplayer_url)
        result_url = '{}?next={}'.format(reverse('account_login'), self.hockeyplayer_url)
        self.assertRedirects(response, result_url)

    def test_get(self):
        response = self.client.get(self.hockeyplayer_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'players/players_update.html')
        context = response.context
        self.assertIsNotNone(context['player'])
        self.assertIsNotNone(context['sport_registration'])
        self.assertIsNotNone(context['form'])

    def test_get_sport_reg_dne(self):
        response = self.client.get(self._format_url(pk=99, player_pk=self.player.pk))
        self.assertEqual(response.status_code, 404)

    def test_get_player_obj_dne(self):
        response = self.client.get(self._format_url(pk=self.sr.pk, player_pk=99))
        self.assertEqual(response.status_code, 404)

    def test_get_not_obj_owner(self):
        self.client.logout()
        user = UserFactory(password=self.password)
        SportRegistrationFactory(user=user, sport=self.ice_hockey)
        self.client.login(email=user.email, password=self.password)
        response = self.client.get(self.hockeyplayer_url)
        self.assertEqual(response.status_code, 404)

    # POST
    def test_post(self):
        self.post_data.update({'jersey_number': 99})
        response = self.client.post(self.hockeyplayer_url, data=self.post_data, follow=True)
        self.assertHasMessage(response, 'Your player information has been updated.')
        self.player.refresh_from_db()
        self.assertEqual(self.player.jersey_number, 99)
        self.assertRedirects(response, self.sr.get_absolute_url())

    def test_post_nothing_changed(self):
        response = self.client.post(self.hockeyplayer_url, data=self.post_data, follow=True)
        self.assertNoMessage(response, 'Your player information has been updated.')
        self.player.refresh_from_db()
        self.assertEqual(self.player.jersey_number, 23)
        self.assertRedirects(response, self.sr.get_absolute_url())

    def test_post_invalid(self):
        self.post_data.update({'position': ''})
        response = self.client.post(self.hockeyplayer_url, data=self.post_data, follow=True)
        self.assertFormError(response, 'form', 'position', 'This field is required.')
        self.assertTemplateUsed('players/players_update.html')

# TODO add tests for other sports
