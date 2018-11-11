from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from ayrabo.utils.urls import url_with_query_string
from common.tests import WaffleSwitchFactory
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from players.tests import BaseballPlayerFactory, HockeyPlayerFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class PlayerUpdateViewTests(BaseTestCase):
    url = 'sports:players:update'

    def setUp(self):
        self.player_update_switch = WaffleSwitchFactory(name='player_update', active=True)
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)

        self.post_data = {
            'jersey_number': 23,
            'position': 'LW',
            'handedness': 'Left'
        }

        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.baseball = SportFactory(name='Baseball')

        self.league = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.division = DivisionFactory(name='Midget Minor AA', league=self.league)
        self.team = TeamFactory(name='Green Machine IceCats', division=self.division)
        self.player = HockeyPlayerFactory(user=self.user, sport=self.ice_hockey, team=self.team, **self.post_data)
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='player')

        self.baseball_league = LeagueFactory(name='Major League Baseball', sport=self.baseball)
        self.baseball_division = DivisionFactory(name='American League East', league=self.baseball_league)
        self.baseball_team = TeamFactory(name='New York Yankees', division=self.baseball_division)
        self.baseball_player = BaseballPlayerFactory(user=self.user, sport=self.baseball, team=self.baseball_team,
                                                     jersey_number=25)

        self.login(user=self.user)

    # General
    def test_login_required(self):
        self.client.logout()
        url = self.format_url(slug='ice-hockey', player_pk=self.player.pk)
        response = self.client.get(url)
        self.assertRedirects(response, self.get_login_required_url(url))

    def test_sport_not_configured(self):
        SportFactory(name='Not Configured', slug='not-configured')
        response = self.client.get(self.format_url(slug='not-configured', player_pk=self.player.pk))
        self.assertTemplateUsed(response, 'sport_not_configured_msg.html')

    def test_sport_dne(self):
        response = self.client.get(self.format_url(slug='non-existent', player_pk=self.player.pk))
        self.assert_404(response)

    def test_has_permission_false(self):
        """
        Make sure the user is the object owner
        """
        self.client.logout()
        user = UserFactory(password=self.password)
        self.login(user=user)
        response = self.client.get(self.format_url(slug='ice-hockey', player_pk=self.player.pk))
        self.assert_404(response)

    def test_player_dne(self):
        response = self.client.get(self.format_url(slug='ice-hockey', player_pk=99))
        self.assert_404(response)

    def test_switch_inactive(self):
        self.player_update_switch.active = False
        self.player_update_switch.save()
        response = self.client.get(self.format_url(slug='ice-hockey', player_pk=self.player.pk))
        self.assert_404(response)

    # GET
    def test_get(self):
        response = self.client.get(self.format_url(slug='ice-hockey', player_pk=self.player.pk))
        context = response.context
        self.assert_200(response)
        self.assertTemplateUsed(response, 'players/players_update.html')
        self.assertEqual(context['player'].pk, self.player.pk)

    # POST
    def test_post(self):
        self.post_data.update({'jersey_number': 99})
        response = self.client.post(self.format_url(slug='ice-hockey', player_pk=self.player.pk), data=self.post_data,
                                    follow=True)
        self.assertHasMessage(response, 'Your player information has been updated.')
        self.player.refresh_from_db()
        self.assertEqual(self.player.jersey_number, 99)
        url = url_with_query_string(reverse('sports:dashboard', kwargs={'slug': self.ice_hockey.slug}), tab='player')
        self.assertRedirects(response, url)

    def test_post_nothing_changed(self):
        response = self.client.post(self.format_url(slug='ice-hockey', player_pk=self.player.pk), data=self.post_data,
                                    follow=True)
        self.assertNoMessage(response, 'Your player information has been updated.')
        self.player.refresh_from_db()
        self.assertEqual(self.player.jersey_number, 23)
        url = url_with_query_string(reverse('sports:dashboard', kwargs={'slug': self.ice_hockey.slug}), tab='player')
        self.assertRedirects(response, url)

    def test_post_invalid(self):
        self.post_data.update({'position': ''})
        response = self.client.post(self.format_url(slug='ice-hockey', player_pk=self.player.pk), data=self.post_data,
                                    follow=True)
        self.assertFormError(response, 'form', 'position', 'This field is required.')
        self.assertTemplateUsed('players/players_update.html')
