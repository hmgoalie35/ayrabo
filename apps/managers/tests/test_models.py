from django.core.validators import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from accounts.tests import UserFactory
from sports.tests import SportRegistrationFactory
from teams.tests import TeamFactory
from .factories.ManagerFactory import ManagerFactory


class ManagerModelTests(TestCase):
    def test_to_string(self):
        manager = ManagerFactory()
        self.assertEqual(str(manager), 'Manager {last_name}'.format(last_name=manager.user.last_name))

    def test_manager_unique_to_team(self):
        user = UserFactory()
        team = TeamFactory(name='Green Machine IceCats')
        ManagerFactory(user=user, team=team)
        with self.assertRaisesMessage(IntegrityError,
                                      'UNIQUE constraint failed: managers_manager.user_id, managers_manager.team_id'):
            ManagerFactory(user=user, team=team)

    def test_create_manager_user_missing_manager_role(self):
        user = UserFactory()
        team = TeamFactory(name='Green Machine IceCats')
        sr = SportRegistrationFactory(user=user, sport=team.division.league.sport)
        sr.set_roles(['Player', 'Referee'])
        manager = ManagerFactory(user=user, team=team)
        with self.assertRaisesMessage(ValidationError,
                                      '{user} - {sport} might not have a sportregistration object or the sportregistration object does not have the manager role assigned'.format(
                                              user=user.email, sport=team.division.league.sport.name)):
            manager.clean()
