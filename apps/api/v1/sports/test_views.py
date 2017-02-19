from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from accounts.tests import UserFactory
from sports.models import SportRegistration
from sports.tests import SportRegistrationFactory


class RemoveSportRegistrationRoleAPIViewTests(APITestCase):
    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)
        self.sr = SportRegistrationFactory(user=self.user)
        self.sr.set_roles(['Player', 'Coach', 'Manager'])

        self.client.login(email=self.email, password=self.password)

    def test_pk_dne(self):
        response = self.client.patch(reverse('v1:sportregistrations:remove_role', kwargs={'pk': 100, 'role': 'player'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_not_object_owner(self):
        other_user = UserFactory()
        sr = SportRegistrationFactory(user=other_user)
        response = self.client.patch(
                reverse('v1:sportregistrations:remove_role', kwargs={'pk': sr.pk, 'role': 'player'}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual({'detail': 'You do not have permission to perform this action.'}, response.data)

    def test_role_removed(self):
        response = self.client.patch(
                reverse('v1:sportregistrations:remove_role', kwargs={'pk': self.sr.pk, 'role': 'player'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual({'detail': 'player role successfully removed.'}, response.data)
        # Need to refetch the object in order to see the changes
        self.assertNotIn('Player', SportRegistration.objects.get(pk=self.sr.pk).roles)

    def test_sportregistration_doesnt_have_role(self):
        response = self.client.patch(
                reverse('v1:sportregistrations:remove_role', kwargs={'pk': self.sr.pk, 'role': 'referee'}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual({'error': 'You are not currently registered as a referee'}, response.data)

    def test_remove_last_role(self):
        self.sr.set_roles(['Player'])
        response = self.client.patch(
                reverse('v1:sportregistrations:remove_role', kwargs={'pk': self.sr.pk, 'role': 'player'}))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
                {'error': 'You cannot remove the player role. You must be registered for at least one role.'},
                response.data)
