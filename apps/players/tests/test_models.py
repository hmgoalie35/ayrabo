from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from accounts.tests import UserFactory
from sports.tests import SportRegistrationFactory
from .factories.PlayerFactory import HockeyPlayerFactory, BaseballPlayerFactory, BasketballPlayerFactory


class PlayerModelTests(TestCase):
    """
    The tests in this class are testing the shared functionality the abstract Player class provides to subclasses.
    Subclasses shouldn't need to test the fields, properties, etc of the Player class as all of that is handled by this
    class

    NOTE: We can't create instances of PlayerFactory so just use any factory that is a subclass. In this case it is
    HockeyPlayerFactory. Nothing specific to HockeyPlayerFactory is being tested in this class.
    """

    def setUp(self):
        self.player = HockeyPlayerFactory()

    def test_league_property(self):
        self.assertEqual(self.player.league, self.player.team.division.league.full_name)

    def test_division_property(self):
        self.assertEqual(self.player.division, self.player.team.division.name)

    def test_max_jersey_number(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is less than or equal to 99.'):
            HockeyPlayerFactory(jersey_number=100).full_clean()

    def test_min_jersey_number(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is greater than or equal to 0.'):
            HockeyPlayerFactory(jersey_number=-1).full_clean()

    def test_to_string(self):
        self.assertEqual(str(self.player), self.player.user.get_full_name())

    def test_unique_with_sport(self):
        with self.assertRaises(IntegrityError):
            HockeyPlayerFactory(user=self.player.user, sport=self.player.sport)

    def test_unique_with_team(self):
        with self.assertRaises(IntegrityError):
            HockeyPlayerFactory(user=self.player.user, team=self.player.team)

    def test_create_player_user_missing_player_role(self):
        user = UserFactory()
        sport = self.player.team.division.league.sport
        sr = SportRegistrationFactory(user=user, sport=sport)
        sr.set_roles(['Referee'])
        player = HockeyPlayerFactory(user=user, sport=sport, team=self.player.team)
        with self.assertRaisesMessage(ValidationError,
                                      '{user} - {sport} might not have a sportregistration object or the sportregistration object does not have the player role assigned'.format(
                                              user=user.email, sport=sport)):
            player.clean()


class HockeyPlayesrodelTests(TestCase):
    def setUp(self):
        self.jersey_number = 35
        self.hockey_player = HockeyPlayerFactory(jersey_number=self.jersey_number)

    def test_duplicate_jersey_number(self):
        validation_msg = 'Please choose another number, {jersey_number} is currently unavailable for {team}'.format(
                jersey_number=self.jersey_number, team=self.hockey_player.team)
        with self.assertRaisesMessage(ValidationError, validation_msg):
            HockeyPlayerFactory(team=self.hockey_player.team, jersey_number=self.jersey_number).full_clean()

    def test_different_jersey_numbers(self):
        jersey_number = 23
        another_hockey_player = HockeyPlayerFactory(team=self.hockey_player.team, jersey_number=jersey_number)
        self.assertEqual(another_hockey_player.jersey_number, jersey_number)

    def test_create_player_user_missing_player_role(self):
        user = UserFactory()
        sport = self.hockey_player.team.division.league.sport
        sr = SportRegistrationFactory(user=user, sport=sport)
        sr.set_roles(['Referee'])
        player = HockeyPlayerFactory(user=user, sport=sport, team=self.hockey_player.team)
        with self.assertRaisesMessage(ValidationError,
                                      '{user} - {sport} might not have a sportregistration object or the sportregistration object does not have the player role assigned'.format(
                                              user=user.email, sport=sport)):
            player.clean()


class BaseballPlayesrodelTests(TestCase):
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
        another_baseball_player = BaseballPlayerFactory(team=self.baseball_player.team, jersey_number=jersey_number)
        self.assertEqual(another_baseball_player.jersey_number, jersey_number)

    def test_create_player_user_missing_player_role(self):
        user = UserFactory()
        sport = self.baseball_player.team.division.league.sport
        sr = SportRegistrationFactory(user=user, sport=sport)
        sr.set_roles(['Referee'])
        player = BaseballPlayerFactory(user=user, sport=sport, team=self.baseball_player.team)
        with self.assertRaisesMessage(ValidationError,
                                      '{user} - {sport} might not have a sportregistration object or the sportregistration object does not have the player role assigned'.format(
                                              user=user.email, sport=sport)):
            player.clean()


class BasketballPlayesrodelTests(TestCase):
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
        another_basketball_player = BasketballPlayerFactory(team=self.basketball_player.team,
                                                            jersey_number=jersey_number)
        self.assertEqual(another_basketball_player.jersey_number, jersey_number)

    def test_create_player_user_missing_player_role(self):
        user = UserFactory()
        sport = self.basketball_player.team.division.league.sport
        sr = SportRegistrationFactory(user=user, sport=sport)
        sr.set_roles(['Referee'])
        player = BasketballPlayerFactory(user=user, sport=sport, team=self.basketball_player.team)
        with self.assertRaisesMessage(ValidationError,
                                      '{user} - {sport} might not have a sportregistration object or the sportregistration object does not have the player role assigned'.format(
                                              user=user.email, sport=sport)):
            player.clean()
