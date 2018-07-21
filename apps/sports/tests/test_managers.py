from django.db import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from users.tests import UserFactory


class SportRegistrationManagerTests(BaseTestCase):
    def setUp(self):
        self.user = UserFactory()
        self.ice_hockey = SportFactory()

    def test_roles_empty(self):
        sport_registrations = SportRegistration.objects.create_for_user_and_sport(self.user, self.ice_hockey, [])
        self.assertListEqual(sport_registrations, [])
        self.assertEqual(SportRegistration.objects.count(), 0)

    def test_roles_non_empty(self):
        roles = ['player', 'coach', 'referee']
        SportRegistration.objects.create_for_user_and_sport(self.user, self.ice_hockey, roles)
        sr = SportRegistration.objects.first()
        self.assertEqual(SportRegistration.objects.count(), 3)
        self.assertTrue(sr.is_complete)
        self.assertEqual(sr.user, self.user)
        self.assertEqual(sr.sport, self.ice_hockey)

    def test_role_already_exists(self):
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='player')
        with self.assertRaises(IntegrityError):
            SportRegistration.objects.create_for_user_and_sport(self.user, self.ice_hockey, roles=['player'])
