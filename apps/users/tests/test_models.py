from django.db import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from organizations.tests import OrganizationFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import PermissionFactory, UserFactory


class PermissionModelTests(BaseTestCase):
    def setUp(self):
        self.user = UserFactory(email='user@ayrabo.com')
        self.team = TeamFactory(name='Long Beach Sharks')
        self.permission = PermissionFactory(user=self.user, name='admin', content_object=self.team)

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            PermissionFactory(user=self.user, name='admin', content_object=self.team)

    def test_to_string(self):
        self.assertEqual(str(self.permission), '<user@ayrabo.com> team admin')


class UserModelTests(BaseTestCase):
    def setUp(self):
        self.user = UserFactory()
        self.organization = OrganizationFactory(name='Long Beach Sharks')

    def test_has_object_permission_true(self):
        PermissionFactory(user=self.user, name='admin', content_object=self.organization)
        self.assertTrue(self.user.has_object_permission('admin', self.organization))

    def test_has_object_permission_false(self):
        self.assertFalse(self.user.has_object_permission('admin', self.organization))

    def test_get_sport_registrations(self):
        ice_hockey = SportFactory(name='Ice Hockey')
        baseball = SportFactory(name='Baseball')
        # Sport reg for another user (should be excluded)
        SportRegistrationFactory()
        # Legacy sport registrations (should be excluded)
        SportRegistrationFactory(user=self.user, sport=ice_hockey, role=None, roles_mask=1)
        SportRegistrationFactory(user=self.user, sport=baseball, role=None, roles_mask=1)
        # New type of sport registrations
        sr1 = SportRegistrationFactory(user=self.user, sport=ice_hockey, role='player')
        sr2 = SportRegistrationFactory(user=self.user, sport=ice_hockey, role='coach')
        sr3 = SportRegistrationFactory(user=self.user, sport=baseball, role='referee')
        registrations = list(self.user.get_sport_registrations())
        # Sport registrations should be sorted by sport and then role
        self.assertListEqual(registrations, [sr3, sr2, sr1])

    def test_sport_registration_data_by_sport(self):
        pass

    def test_sport_registration_data_by_sport_no_registrations(self):
        pass

    def test_sport_registration_data_by_sport_legacy_registrations(self):
        pass

    def test_sport_registration_data_no_role_objects(self):
        pass

    def test_get_roles(self):
        pass

    def test_get_players(self):
        pass

    def test_get_coaches(self):
        pass

    def test_get_referees(self):
        pass

    def test_get_managers(self):
        pass

    def test_get_scorekeepers(self):
        pass
