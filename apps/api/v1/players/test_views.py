from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from accounts.tests import UserFactory
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from players.tests import HockeyPlayerFactory
from sports.tests import SportRegistrationFactory, SportFactory
from teams.tests import TeamFactory


# TODO Add tests for other player types.
class DeactivatePlayerApiViewTests(APITestCase):
    def _format_url(self, **kwargs):
        return reverse(self.url, kwargs=kwargs)

    def setUp(self):
        self.url = 'v1:sportregistrations:players:deactivate'
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)

        self.sport = SportFactory(name='Ice Hockey')
        self.league = LeagueFactory(sport=self.sport, full_name='National Hockey League')
        self.division = DivisionFactory(league=self.league, name='Atlantic Division')
        self.team = TeamFactory(division=self.division, name='Boston Bruins')
        self.player = HockeyPlayerFactory(user=self.user, team=self.team, sport=self.sport)

        self.sr = SportRegistrationFactory(user=self.user, sport=self.sport)
        self.sr.set_roles(['Player', 'Referee'])

        self.client.login(email=self.email, password=self.password)

    def test_anonymous(self):
        self.client.logout()
        response = self.client.patch(self._format_url(pk=self.sr.pk, player_pk=self.player.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

    def test_not_sport_registration_owner(self):
        sr = SportRegistrationFactory()
        response = self.client.patch(self._format_url(pk=sr.pk, player_pk=self.player.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'You do not have permission to perform this action.'})

    def test_not_player_owner(self):
        player = HockeyPlayerFactory()
        response = self.client.patch(self._format_url(pk=self.sr.pk, player_pk=player.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'You do not have permission to perform this action.'})

    def test_sport_registration_pk_dne(self):
        response = self.client.patch(self._format_url(pk=888, player_pk=self.player.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.data, {'detail': 'Not found.'})

    def test_player_pk_dne(self):
        response = self.client.patch(self._format_url(pk=self.sr.pk, player_pk=888))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.data, {'detail': 'Not found.'})

    def test_deactivates_player(self):
        response = self.client.patch(self._format_url(pk=self.sr.pk, player_pk=self.player.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.player.refresh_from_db(fields=['is_active'])
        self.assertFalse(self.player.is_active)

    def test_last_player_registration_remove_role(self):
        """
        If trying to deactivate the last player registration,
        the player role should be removed from the sport registration
        """
        response = self.client.patch(self._format_url(pk=self.sr.pk, player_pk=self.player.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sr.refresh_from_db()
        self.assertFalse(self.sr.has_role('Player'))

    def test_remove_last_role(self):
        self.sr.set_roles(['Player'])
        response = self.client.patch(self._format_url(pk=self.sr.pk, player_pk=self.player.pk))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
                response.data,
                {'error': 'You cannot remove the player role. You must be registered for at least one role.'})
