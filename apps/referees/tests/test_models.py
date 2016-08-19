from django.core.validators import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from accounts.tests import UserFactory
from leagues.tests import LeagueFactory
from sports.tests import SportRegistrationFactory
from .factories.RefereeFactory import RefereeFactory


class RefereeModelTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.league = LeagueFactory(full_name='Long Island Amateur Hockey League')

    def test_to_string(self):
        referee = RefereeFactory()
        self.assertEqual(str(referee), 'Referee {full_name}'.format(full_name=referee.user.get_full_name()))

    def test_referee_unique_to_league(self):
        RefereeFactory(user=self.user, league=self.league)
        with self.assertRaises(IntegrityError):
            RefereeFactory(user=self.user, league=self.league)

    def test_create_referee_user_missing_referee_role(self):
        sr = SportRegistrationFactory(user=self.user, sport=self.league.sport)
        sr.set_roles(['Player'])
        referee = RefereeFactory(user=self.user, league=self.league)
        with self.assertRaisesMessage(ValidationError,
                                      '{user} - {sport} might not have a sportregistration object or the sportregistration object does not have the referee role assigned'.format(
                                              user=self.user.email, sport=self.league.sport.name)):
            referee.clean()
