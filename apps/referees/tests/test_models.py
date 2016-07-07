from django.core.validators import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from accounts.tests.factories.UserFactory import UserFactory
from divisions.tests.factories.DivisionFactory import DivisionFactory
from .factories.RefereeFactory import RefereeFactory


class RefereeModelTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.userprofile.set_roles(['Referee'])
        self.division = DivisionFactory(name='Midget Minor AA')

    def test_to_string(self):
        referee = RefereeFactory()
        self.assertEqual(str(referee), 'Referee {full_name}'.format(full_name=referee.user.get_full_name()))

    def test_referee_unique_to_division(self):
        RefereeFactory(user=self.user, division=self.division)
        with self.assertRaises(IntegrityError,
                               msg=' UNIQUE constraint failed: referees_referee.user_id, referees_referee.division_id'):
            RefereeFactory(user=self.user, division=self.division)

    def test_create_referee_user_missing_referee_role(self):
        self.user.userprofile.set_roles(['Player'])
        referee = RefereeFactory(user=self.user, division=self.division)
        with self.assertRaises(ValidationError,
                               msg='{full_name} does not have the referee role assigned, please update their userprofile to include it'.format(
                                       full_name=self.user.get_full_name())):
            referee.clean()
