from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from users.tests import UserFactory
from coaches.tests import CoachFactory
from sports.tests import SportRegistrationFactory


class DeactivateCoachApiViewTests(APITestCase):
    def _format_url(self, **kwargs):
        return reverse(self.url, kwargs=kwargs)

    def setUp(self):
        self.url = 'v1:sportregistrations:coaches:deactivate'
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)
        self.sr = SportRegistrationFactory(user=self.user)
        self.sr.set_roles(['Player', 'Coach'])

        self.coach = CoachFactory(user=self.user)

        self.client.login(email=self.email, password=self.password)

    def test_anonymous(self):
        self.client.logout()
        response = self.client.patch(self._format_url(pk=self.sr.pk, coach_pk=self.coach.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

    def test_not_sport_registration_owner(self):
        sr = SportRegistrationFactory()
        response = self.client.patch(self._format_url(pk=sr.pk, coach_pk=self.coach.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'You do not have permission to perform this action.'})

    def test_not_coach_owner(self):
        coach = CoachFactory()
        response = self.client.patch(self._format_url(pk=self.sr.pk, coach_pk=coach.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'You do not have permission to perform this action.'})

    def test_sport_registration_pk_dne(self):
        response = self.client.patch(self._format_url(pk=888, coach_pk=self.coach.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.data, {'detail': 'Not found.'})

    def test_coach_pk_dne(self):
        response = self.client.patch(self._format_url(pk=self.sr.pk, coach_pk=888))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.data, {'detail': 'Not found.'})

    def test_deactivates_coach(self):
        response = self.client.patch(self._format_url(pk=self.sr.pk, coach_pk=self.coach.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.coach.refresh_from_db(fields=['is_active'])
        self.assertFalse(self.coach.is_active)

    def test_last_coach_registration_remove_role(self):
        """
        If trying to deactivate the last coach registration,
        the coach role should be removed from the sport registration
        """
        response = self.client.patch(self._format_url(pk=self.sr.pk, coach_pk=self.coach.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sr.refresh_from_db()
        self.assertFalse(self.sr.has_role('Coach'))

    def test_remove_last_role(self):
        self.sr.set_roles(['Coach'])
        response = self.client.patch(self._format_url(pk=self.sr.pk, coach_pk=self.coach.pk))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
                response.data,
                {'error': 'You cannot remove the coach role. You must be registered for at least one role.'})
