from rest_framework import status

from accounts.tests import UserFactory
from ayrabo.utils.testing import BaseAPITestCase
from scorekeepers.tests import ScorekeeperFactory
from sports.tests import SportRegistrationFactory


class DeactivateScorekeeperApiViewTests(BaseAPITestCase):
    url = 'v1:sportregistrations:scorekeepers:deactivate'

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)
        self.sr = SportRegistrationFactory(user=self.user)
        self.sr.set_roles(['Player', 'Referee', 'Scorekeeper'])

        self.scorekeeper = ScorekeeperFactory(user=self.user)

        self.client.login(email=self.email, password=self.password)

    def test_anonymous(self):
        self.client.logout()
        response = self.client.patch(self.format_url(pk=self.sr.pk, scorekeeper_pk=self.scorekeeper.pk))
        self.assertAPIError(response, 'unauthenticated')

    def test_not_sport_registration_owner(self):
        sr = SportRegistrationFactory()
        response = self.client.patch(self.format_url(pk=sr.pk, scorekeeper_pk=self.scorekeeper.pk))
        self.assertAPIError(response, 'permission_denied')

    def test_not_scorekeeper_owner(self):
        scorekeeper = ScorekeeperFactory()
        response = self.client.patch(self.format_url(pk=self.sr.pk, scorekeeper_pk=scorekeeper.pk))
        self.assertAPIError(response, 'permission_denied')

    def test_sport_registration_pk_dne(self):
        response = self.client.patch(self.format_url(pk=888, scorekeeper_pk=self.scorekeeper.pk))
        self.assertAPIError(response, 'not_found')

    def test_scorekeeper_pk_dne(self):
        response = self.client.patch(self.format_url(pk=self.sr.pk, scorekeeper_pk=888))
        self.assertAPIError(response, 'not_found')

    def test_deactivates_scorekeeper(self):
        response = self.client.patch(self.format_url(pk=self.sr.pk, scorekeeper_pk=self.scorekeeper.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.scorekeeper.refresh_from_db(fields=['is_active'])
        self.assertFalse(self.scorekeeper.is_active)

    def test_last_scorekeeper_registration_remove_role(self):
        """
        If trying to deactivate the last scorekeeper registration,
        the scorekeeper role should be removed from the sport registration
        """
        response = self.client.patch(self.format_url(pk=self.sr.pk, scorekeeper_pk=self.scorekeeper.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sr.refresh_from_db()
        self.assertFalse(self.sr.has_role('Scorekeeper'))

    def test_remove_last_role(self):
        self.sr.set_roles(['Scorekeeper'])
        response = self.client.patch(self.format_url(pk=self.sr.pk, scorekeeper_pk=self.scorekeeper.pk))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.data,
            {'error': 'You cannot remove the scorekeeper role. You must be registered for at least one role.'})
