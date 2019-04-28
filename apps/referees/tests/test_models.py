from django.db.utils import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory
from referees.tests import RefereeFactory
from users.tests import UserFactory


class RefereeModelTests(BaseTestCase):
    def setUp(self):
        self.user = UserFactory(first_name='Zebra', last_name='Stripes')
        self.league = LeagueFactory(name='Long Island Amateur Hockey League')

    def test_to_string(self):
        referee = RefereeFactory(user=self.user)
        self.assertEqual(str(referee), 'Referee Zebra Stripes')

    def test_referee_unique_to_league(self):
        RefereeFactory(user=self.user, league=self.league)
        with self.assertRaises(IntegrityError):
            RefereeFactory(user=self.user, league=self.league)
