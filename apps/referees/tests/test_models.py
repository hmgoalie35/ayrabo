from django.db.utils import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory
from users.tests import UserFactory
from .factories.RefereeFactory import RefereeFactory


class RefereeModelTests(BaseTestCase):
    def setUp(self):
        self.user = UserFactory()
        self.league = LeagueFactory(name='Long Island Amateur Hockey League')

    def test_to_string(self):
        referee = RefereeFactory()
        self.assertEqual(str(referee), 'Referee {full_name}'.format(full_name=referee.user.get_full_name()))

    def test_referee_unique_to_league(self):
        RefereeFactory(user=self.user, league=self.league)
        with self.assertRaises(IntegrityError):
            RefereeFactory(user=self.user, league=self.league)
