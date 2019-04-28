from django.db.utils import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from coaches.tests import CoachFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class CoachModelTests(BaseTestCase):
    def test_to_string(self):
        first_name = 'Herb'
        last_name = 'Brooks'
        user = UserFactory(first_name=first_name, last_name=last_name)
        coach = CoachFactory(user=user)
        self.assertEqual(str(coach), 'Coach {}'.format(last_name))

    def test_coach_unique_to_team(self):
        user = UserFactory()
        team = TeamFactory(name='Green Machine IceCats')
        CoachFactory(user=user, team=team)
        with self.assertRaises(IntegrityError):
            CoachFactory(user=user, team=team)
