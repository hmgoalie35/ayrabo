from django.core.validators import ValidationError
from django.db.utils import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from sports.tests import SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory
from .factories.CoachFactory import CoachFactory


class CoachModelTests(BaseTestCase):
    def test_to_string(self):
        coach = CoachFactory.create()
        self.assertEqual(str(coach), 'Coach {last_name}'.format(last_name=coach.user.last_name))

    def test_coach_unique_to_team(self):
        user = UserFactory.create()
        team = TeamFactory(name='Green Machine IceCats')
        CoachFactory.create(user=user, team=team)
        with self.assertRaises(IntegrityError):
            CoachFactory.create(user=user, team=team)

    def test_create_coach_user_missing_coach_role(self):
        user = UserFactory.create()
        team = TeamFactory(name='Green Machine IceCats')
        SportRegistrationFactory(user=user, sport=team.division.league.sport, role='player')
        coach = CoachFactory.create(user=user, team=team)
        with self.assertRaisesMessage(ValidationError,
                                      '{} - {} might not have a sportregistration object or the '
                                      'sportregistration object does not have the coach role assigned'.format(
                                          user.email, team.division.league.sport.name)):
            coach.clean()
