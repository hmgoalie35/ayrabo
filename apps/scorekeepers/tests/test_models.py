from django.db import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from scorekeepers.tests import ScorekeeperFactory
from sports.tests import SportFactory
from users.tests import UserFactory


class ScorekeeperModelTests(BaseTestCase):
    def setUp(self):
        self.user = UserFactory(email='h@p.com')
        self.sport = SportFactory(name='Ice Hockey')

    def test_to_string(self):
        scorekeeper = ScorekeeperFactory(user=self.user, sport=self.sport)
        self.assertEqual(str(scorekeeper), 'h@p.com - Ice Hockey')

    def test_scorekeeper_unique_to_sport(self):
        ScorekeeperFactory(user=self.user, sport=self.sport)
        with self.assertRaises(IntegrityError):
            ScorekeeperFactory(user=self.user, sport=self.sport)
