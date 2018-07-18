from django.core.exceptions import ValidationError
from django.db import IntegrityError

from users.tests import UserFactory
from ayrabo.utils.testing import BaseTestCase
from scorekeepers.tests import ScorekeeperFactory
from sports.tests import SportFactory, SportRegistrationFactory


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

    def test_user_missing_scorekeeper_role(self):
        SportRegistrationFactory(user=self.user, sport=self.sport, role='player')
        scorekeeper = ScorekeeperFactory(user=self.user, sport=self.sport)
        with self.assertRaisesMessage(ValidationError, 'h@p.com - Ice Hockey might not have a sportregistration object '
                                                       'or the sportregistration object does not have the scorekeeper '
                                                       'role assigned'):
            scorekeeper.clean()
