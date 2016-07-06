from django.core.validators import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from accounts.tests.factories.UserFactory import UserFactory
from teams.tests.factories.TeamFactory import TeamFactory
from .factories.ManagerFactory import ManagerFactory


class ManagerModelTests(TestCase):
    def test_to_string(self):
        manager = ManagerFactory()
        self.assertEqual(str(manager), 'Manager {full_name}'.format(full_name=manager.user.get_full_name()))

    def test_manager_unique_to_team(self):
        user = UserFactory()
        team = TeamFactory(name='Green Machine IceCats')
        ManagerFactory(user=user, team=team)
        with self.assertRaises(IntegrityError,
                               msg='UNIQUE constraint failed: managers_manager.user_id, managers_manager.team_id'):
            ManagerFactory(user=user, team=team)

    def test_create_manager_user_missing_manager_role(self):
        user = UserFactory()
        user.userprofile.set_roles(['Player', 'Referee'])
        team = TeamFactory(name='Green Machine IceCats')
        manager = ManagerFactory(user=user, team=team)
        with self.assertRaises(ValidationError,
                               msg='{full_name} does not have the manager role assigned, please update their userprofile to include it'.format(
                                       full_name=user.get_full_name())):
            manager.clean()
