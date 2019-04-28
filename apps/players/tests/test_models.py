from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from players.tests import BaseballPlayerFactory, BasketballPlayerFactory, HockeyPlayerFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class AbstractPlayerModelTests(BaseTestCase):
    """
    The tests in this class are testing the shared functionality the abstract Player class provides to subclasses.
    Subclasses shouldn't need to test the fields, properties, etc of the Player class as all of that is handled by this
    class

    NOTE: We can't create instances of PlayerFactory so just use any factory that is a subclass. In this case it is
    HockeyPlayerFactory. Nothing specific to HockeyPlayerFactory is being tested in this class.
    """

    def setUp(self):
        self.user = UserFactory(first_name='Robin', last_name='Lehner')
        self.player = HockeyPlayerFactory(user=self.user)

    def test_league_property(self):
        self.assertEqual(self.player.league, self.player.team.division.league)

    def test_division_property(self):
        self.assertEqual(self.player.division, self.player.team.division)

    def test_max_jersey_number(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is less than or equal to 99.'):
            HockeyPlayerFactory(jersey_number=100).full_clean()

    def test_min_jersey_number(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is greater than or equal to 0.'):
            HockeyPlayerFactory(jersey_number=-1).full_clean()

    def test_to_string(self):
        self.assertEqual(str(self.player), 'Robin Lehner')

    def test_unique_with_team(self):
        with self.assertRaises(IntegrityError):
            HockeyPlayerFactory(user=self.user, team=self.player.team)

    def test_fields(self):
        t = TeamFactory()
        player = HockeyPlayerFactory(team=t)
        expected = {
            'Team': t,
            'Division': t.division,
            'Jersey Number': player.jersey_number
        }
        fields = player.fields
        # We only want to test the fields from the super class are returned.
        del fields['Position']
        del fields['Handedness']
        self.assertDictEqual(fields, expected)

    def test_table_fields(self):
        t = TeamFactory()
        user = UserFactory(first_name='Michael', last_name='Scott')
        player = HockeyPlayerFactory(team=t, jersey_number=1, user=user, handedness='Left', position='G')
        fields = player.table_fields
        del fields['Position']
        del fields['Handedness']
        self.assertDictEqual(fields, {
            'Jersey Number': 1,
            'Name': 'Michael Scott',
        })


class HockeyPlayerModelTests(BaseTestCase):
    def setUp(self):
        self.jersey_number = 35
        user = UserFactory(first_name='Michael', last_name='Scott')
        self.hockey_player = HockeyPlayerFactory(jersey_number=self.jersey_number, user=user, handedness='Left',
                                                 position='G')

    def test_duplicate_jersey_number(self):
        validation_msg = 'Please choose another number, {jersey_number} is currently unavailable for {team}'.format(
            jersey_number=self.jersey_number, team=self.hockey_player.team)
        with self.assertRaisesMessage(ValidationError, validation_msg):
            HockeyPlayerFactory(team=self.hockey_player.team, jersey_number=self.jersey_number).full_clean()

    def test_different_jersey_numbers(self):
        jersey_number = 23
        # Error shouldn't be thrown...
        p = HockeyPlayerFactory(team=self.hockey_player.team, jersey_number=jersey_number, is_active=False)
        p.clean()
        another_hockey_player = HockeyPlayerFactory(team=self.hockey_player.team, jersey_number=jersey_number)
        another_hockey_player.clean()
        self.assertEqual(another_hockey_player.jersey_number, jersey_number)

    def test_fields(self):
        t = TeamFactory()
        player = HockeyPlayerFactory(team=t)
        expected = {
            'Team': t,
            'Division': t.division,
            'Jersey Number': player.jersey_number,
            'Position': player.get_position_display(),
            'Handedness': player.get_handedness_display()
        }
        fields = player.fields
        self.assertDictEqual(expected, fields)

    def test_table_fields(self):
        self.assertDictEqual(self.hockey_player.table_fields, {
            'Jersey Number': self.jersey_number,
            'Name': 'Michael Scott',
            'Position': 'Goaltender',
            'Handedness': 'Left'
        })


class BaseballPlayerModelTests(BaseTestCase):
    def setUp(self):
        self.jersey_number = 35
        self.baseball_player = BaseballPlayerFactory(jersey_number=self.jersey_number)

    def test_duplicate_jersey_number(self):
        validation_msg = 'Please choose another number, {jersey_number} is currently unavailable for {team}'.format(
            jersey_number=self.jersey_number, team=self.baseball_player.team)
        with self.assertRaisesMessage(ValidationError, validation_msg):
            BaseballPlayerFactory(team=self.baseball_player.team, jersey_number=self.jersey_number).full_clean()

    def test_different_jersey_numbers(self):
        jersey_number = 23
        b = BaseballPlayerFactory(team=self.baseball_player.team, jersey_number=jersey_number, is_active=False)
        b.clean()
        another_baseball_player = BaseballPlayerFactory(team=self.baseball_player.team, jersey_number=jersey_number)
        another_baseball_player.clean()
        self.assertEqual(another_baseball_player.jersey_number, jersey_number)

    def test_fields(self):
        t = TeamFactory()
        player = BaseballPlayerFactory(team=t)
        expected = {
            'Team': t,
            'Division': t.division,
            'Jersey Number': player.jersey_number,
            'Position': player.get_position_display(),
            'Catches': player.get_catches_display(),
            'Bats': player.get_bats_display()
        }
        fields = player.fields
        self.assertDictEqual(expected, fields)

    def test_table_fields(self):
        user = UserFactory(first_name='Dwight', last_name='Schrute')
        player = BaseballPlayerFactory(user=user, jersey_number=self.jersey_number, position='C', catches='Left',
                                       bats='Left')
        self.assertDictEqual(player.table_fields, {
            'Jersey Number': 35,
            'Name': 'Dwight Schrute',
            'Position': 'Catcher',
            'Catches': 'Left',
            'Bats': 'Left'
        })


class BasketballPlayerModelTests(BaseTestCase):
    def setUp(self):
        self.jersey_number = 35
        self.basketball_player = BasketballPlayerFactory(jersey_number=self.jersey_number)

    def test_duplicate_jersey_number(self):
        validation_msg = 'Please choose another number, {jersey_number} is currently unavailable for {team}'.format(
            jersey_number=self.jersey_number, team=self.basketball_player.team)
        with self.assertRaisesMessage(ValidationError, validation_msg):
            BasketballPlayerFactory(team=self.basketball_player.team, jersey_number=self.jersey_number).full_clean()

    def test_different_jersey_numbers(self):
        jersey_number = 23
        b = BasketballPlayerFactory(team=self.basketball_player.team, jersey_number=jersey_number, is_active=False)
        b.clean()
        another_basketball_player = BasketballPlayerFactory(team=self.basketball_player.team,
                                                            jersey_number=jersey_number)
        another_basketball_player.clean()
        self.assertEqual(another_basketball_player.jersey_number, jersey_number)

    def test_fields(self):
        t = TeamFactory()
        player = BasketballPlayerFactory(team=t)
        expected = {
            'Team': t,
            'Division': t.division,
            'Jersey Number': player.jersey_number,
            'Position': player.get_position_display(),
            'Shoots': player.get_shoots_display(),
        }
        fields = player.fields
        self.assertDictEqual(expected, fields)

    def test_table_fields(self):
        user = UserFactory(first_name='Ryan', last_name='Howard')
        player = BasketballPlayerFactory(user=user, jersey_number=self.jersey_number, position='PG', shoots='Left')
        self.assertDictEqual(player.table_fields, {
            'Jersey Number': 35,
            'Name': 'Ryan Howard',
            'Position': 'Point Guard',
            'Shoots': 'Left',
        })
