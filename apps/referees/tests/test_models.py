from django.core.validators import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from accounts.tests.factories.UserFactory import UserFactory
from leagues.tests.factories.LeagueFactory import LeagueFactory
from userprofiles.tests.factories.RolesMaskFactory import RolesMaskFactory
from .factories.RefereeFactory import RefereeFactory


class RefereeModelTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.userprofile.set_roles(['Referee'])
        self.league = LeagueFactory(full_name='Long Island Amateur Hockey League')

    def test_to_string(self):
        referee = RefereeFactory()
        self.assertEqual(str(referee), 'Referee {full_name}'.format(full_name=referee.user.get_full_name()))

    def test_referee_unique_to_league(self):
        RefereeFactory(user=self.user, league=self.league)
        with self.assertRaises(IntegrityError,
                               msg=' UNIQUE constraint failed: referees_referee.user_id, referees_referee.league_id'):
            RefereeFactory(user=self.user, league=self.league)

    def test_create_referee_user_missing_referee_role(self):
        rm = RolesMaskFactory(user=self.user, sport=self.league.sport)
        rm.set_roles(['Player'])
        referee = RefereeFactory(user=self.user, league=self.league)
        with self.assertRaises(ValidationError,
                               msg='{user} - {sport} might not have a rolesmask object or the rolesmask object does not have the referee role assigned'.format(
                                       user=self.user.email, sport=self.league.sport.name)):
            referee.clean()
