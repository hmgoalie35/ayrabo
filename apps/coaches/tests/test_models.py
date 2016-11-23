from django.core.validators import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from accounts.tests import UserFactory
from sports.tests import SportRegistrationFactory
from teams.tests import TeamFactory
from .factories.CoachFactory import CoachFactory


class CoachModelTests(TestCase):
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
        sr = SportRegistrationFactory(user=user, sport=team.division.league.sport)
        sr.set_roles(['Player', 'Referee'])
        coach = CoachFactory.create(user=user, team=team)
        with self.assertRaisesMessage(ValidationError,
                                      '{user} - {sport} might not have a sportregistration object or the '
                                      'sportregistration object does not have the coach role assigned'.format(
                                              user=user.email, sport=team.division.league.sport.name)):
            coach.clean()
