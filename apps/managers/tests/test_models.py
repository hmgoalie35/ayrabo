from django.db import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from managers.tests import ManagerFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class ManagerModelTests(BaseTestCase):
    def test_to_string(self):
        manager = ManagerFactory()
        self.assertEqual(str(manager), 'Manager {last_name}'.format(last_name=manager.user.last_name))

    def test_manager_unique_to_team(self):
        user = UserFactory()
        team = TeamFactory(name='Green Machine IceCats')
        ManagerFactory(user=user, team=team)
        with self.assertRaises(IntegrityError):
            ManagerFactory(user=user, team=team)
