import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from ayrabo.utils.urls import url_with_query_string
from common.tests import WaffleSwitchFactory
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from players.models import HockeyPlayer
from players.tests import BaseballPlayerFactory, HockeyPlayerFactory
from sports.models import SportRegistration
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
            'position': HockeyPlayer.LEFT_WING,
            'handedness': HockeyPlayer.LEFT,
        }

        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.baseball = SportFactory(name='Baseball')

        self.league = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.division = DivisionFactory(name='Midget Minor AA', league=self.league)
        self.team = TeamFactory(name='Green Machine IceCats', division=self.division)
        self.player = HockeyPlayerFactory(user=self.user, sport=self.ice_hockey, team=self.team, **self.post_data)
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.PLAYER)

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
        self.assertLoginRequired(url)

    def test_sport_not_configured(self):
        SportFactory(name='Not Configured', slug='not-configured')
        response = self.client.get(self.format_url(slug='not-configured', player_pk=self.player.pk))
        self.assertTemplateUsed(response, 'misconfigurations/base.html')

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


class HockeyProfileAdminBulkUploadViewTests(BaseTestCase):
    url = 'admin:players_hockeyplayer_bulk_upload'

    def setUp(self):
        self.url = self.format_url()
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password, is_staff=True, is_superuser=True)
        self.sport = SportFactory(name='Ice Hockey')
        self.league = LeagueFactory(sport=self.sport)
        self.division = DivisionFactory(league=self.league)
        self.team = TeamFactory(id=136, division=self.division)
        self.user2 = UserFactory(id=3596)

    def test_post_valid_csv(self):
        self.login(user=self.user)
        SportRegistration.objects.create(user=self.user2, sport=self.sport, role=SportRegistration.PLAYER)
        with open(os.path.join(settings.STATIC_DIR, 'csv_examples', 'bulk_upload_hockeyplayers_example.csv')) as f:
            response = self.client.post(self.url, {'file': f}, follow=True)

            player = HockeyPlayer.objects.first()
            sport_registrations = SportRegistration.objects.filter(user=self.user2)

            self.assertHasMessage(response, 'Successfully created 1 hockey player')
            self.assertEqual(player.user, self.user2)
            self.assertEqual(player.sport, self.sport)
            self.assertEqual(player.team, self.team)
            self.assertEqual(player.jersey_number, 99)
            self.assertEqual(player.position, 'LW')
            self.assertEqual(player.handedness, 'Left')
            self.assertEqual(sport_registrations.count(), 1)

    def test_post_invalid_csv(self):
        self.login(email=self.email, password=self.password)
        header = ['user', 'team', 'jersey_number', 'position', 'handedness']
        row = [str(self.user2.pk), '136', '', 'INVALID', 'Right']
        content = f'{",".join(header)}\n{",".join(row)}'.encode()
        f = SimpleUploadedFile('test.csv', content)
        response = self.client.post(self.url, {'file': f}, follow=True)

        self.assertFormsetError(
            response,
            'formset',
            0,
            'jersey_number',
            ['This field is required.']
        )
        self.assertFormsetError(
            response,
            'formset',
            0,
            'position',
            ['Select a valid choice. INVALID is not one of the available choices.']
        )
