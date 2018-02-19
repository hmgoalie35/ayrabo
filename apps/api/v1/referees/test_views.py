from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from users.tests import UserFactory
from referees.tests import RefereeFactory
from sports.tests import SportRegistrationFactory


class DeactivateRefereeApiViewTests(APITestCase):
    def _format_url(self, **kwargs):
        return reverse(self.url, kwargs=kwargs)

    def setUp(self):
        self.url = 'v1:sportregistrations:referees:deactivate'
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)
        self.sr = SportRegistrationFactory(user=self.user)
        self.sr.set_roles(['Player', 'Referee'])

        self.referee = RefereeFactory(user=self.user)

        self.client.login(email=self.email, password=self.password)

    def test_anonymous(self):
        self.client.logout()
        response = self.client.patch(self._format_url(pk=self.sr.pk, referee_pk=self.referee.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

    def test_not_sport_registration_owner(self):
        sr = SportRegistrationFactory()
        response = self.client.patch(self._format_url(pk=sr.pk, referee_pk=self.referee.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'You do not have permission to perform this action.'})

    def test_not_referee_owner(self):
        referee = RefereeFactory()
        response = self.client.patch(self._format_url(pk=self.sr.pk, referee_pk=referee.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'You do not have permission to perform this action.'})

    def test_sport_registration_pk_dne(self):
        response = self.client.patch(self._format_url(pk=888, referee_pk=self.referee.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.data, {'detail': 'Not found.'})

    def test_referee_pk_dne(self):
        response = self.client.patch(self._format_url(pk=self.sr.pk, referee_pk=888))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.data, {'detail': 'Not found.'})

    def test_deactivates_referee(self):
        response = self.client.patch(self._format_url(pk=self.sr.pk, referee_pk=self.referee.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.referee.refresh_from_db(fields=['is_active'])
        self.assertFalse(self.referee.is_active)

    def test_last_referee_registration_remove_role(self):
        """
        If trying to deactivate the last referee registration,
        the referee role should be removed from the sport registration
        """
        response = self.client.patch(self._format_url(pk=self.sr.pk, referee_pk=self.referee.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sr.refresh_from_db()
        self.assertFalse(self.sr.has_role('Referee'))

    def test_remove_last_role(self):
        self.sr.set_roles(['Referee'])
        response = self.client.patch(self._format_url(pk=self.sr.pk, referee_pk=self.referee.pk))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
                response.data,
                {'error': 'You cannot remove the referee role. You must be registered for at least one role.'})
