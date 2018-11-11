from django.db.utils import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from coaches.tests import CoachFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


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
