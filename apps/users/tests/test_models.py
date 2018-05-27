from django.db import IntegrityError

from ayrabo.utils.testing import BaseTestCase
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
