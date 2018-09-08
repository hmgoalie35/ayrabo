from django.db import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from coaches.tests import CoachFactory
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from organizations.tests import OrganizationFactory
from players.tests import HockeyPlayerFactory
from referees.tests import RefereeFactory
from scorekeepers.tests import ScorekeeperFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import PermissionFactory, UserFactory


class PermissionModelTests(BaseTestCase):
    def setUp(self):
        self.user = UserFactory(email='user@ayrabo.com')
        self.team = TeamFactory(name='Long Beach Sharks')
        self.permission = PermissionFactory(user=self.user, name='admin', content_object=self.team)

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            PermissionFactory(user=self.user, name='admin', content_object=self.team)

    def test_to_string(self):
        self.assertEqual(str(self.permission), '<user@ayrabo.com> team admin')


class UserModelTests(BaseTestCase):
    def setUp(self):
        self.user = UserFactory()
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.baseball = SportFactory(name='Baseball')
        self.liahl = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)
        self.team = TeamFactory(name='Green Machine IceCats', division=self.mm_aa)
        # Sport reg for another user (should be excluded)
        SportRegistrationFactory()
        self.organization = OrganizationFactory(name='Long Beach Sharks')

    def test_has_object_permission_true(self):
        PermissionFactory(user=self.user, name='admin', content_object=self.organization)
        self.assertTrue(self.user.has_object_permission('admin', self.organization))

    def test_has_object_permission_false(self):
        self.assertFalse(self.user.has_object_permission('admin', self.organization))

    def test_get_sport_registrations(self):
        # Legacy sport registrations (should be excluded)
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=None, roles_mask=1)
        SportRegistrationFactory(user=self.user, sport=self.baseball, role=None, roles_mask=1)
        # New type of sport registrations
        sr1 = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='player')
        sr2 = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='coach')
        sr3 = SportRegistrationFactory(user=self.user, sport=self.baseball, role='referee')
        registrations = list(self.user.get_sport_registrations())
        # Sport registrations should be sorted by sport and then role
        self.assertListEqual(registrations, [sr3, sr2, sr1])

    def test_sport_registration_data_by_sport(self):
        pass

    def test_sport_registration_data_by_sport_no_registrations(self):
        pass

    def test_sport_registration_data_by_sport_legacy_registrations(self):
        pass

    def test_sport_registration_data_no_role_objects(self):
        pass

    def test_get_roles(self):
        pass

    def test_get_players(self):
        HockeyPlayerFactory(sport=self.ice_hockey, team=self.team)
        team = TeamFactory(division__league__sport=self.ice_hockey)
        HockeyPlayerFactory(user=self.user, sport=self.ice_hockey, team=team, is_active=False)
        player = HockeyPlayerFactory(user=self.user, sport=self.ice_hockey, team=self.team)
        players = self.user.get_players(self.ice_hockey)
        self.assertListEqual(list(players), [player])

    def test_get_players_sport_not_configured(self):
        players = self.user.get_players(SportFactory(name='Invalid Sport'))
        self.assertListEqual(players, [])

    def test_get_coaches(self):
        CoachFactory(team=self.team)
        CoachFactory(user=self.user, team=TeamFactory(division__league__sport=self.baseball))
        CoachFactory(user=self.user, team=TeamFactory(division__league__sport=self.ice_hockey), is_active=False)
        coach = CoachFactory(user=self.user, team=self.team)
        coaches = self.user.get_coaches(self.ice_hockey)
        self.assertListEqual(list(coaches), [coach])

    def test_get_referees(self):
        RefereeFactory(league=self.liahl)
        RefereeFactory(user=self.user, league=LeagueFactory(sport=self.baseball))
        RefereeFactory(user=self.user, league=LeagueFactory(sport=self.ice_hockey), is_active=False)
        referee = RefereeFactory(user=self.user, league=self.liahl)
        referees = self.user.get_referees(self.ice_hockey)
        self.assertListEqual(list(referees), [referee])

    def test_get_managers(self):
        ManagerFactory(team=self.team)
        ManagerFactory(user=self.user, team=TeamFactory(division__league__sport=self.baseball))
        ManagerFactory(user=self.user, team=TeamFactory(division__league__sport=self.ice_hockey), is_active=False)
        manager = ManagerFactory(user=self.user, team=self.team)
        managers = list(self.user.get_managers(self.ice_hockey))
        self.assertListEqual(managers, [manager])

    def test_get_scorekeepers(self):
        # Users can only be registered as a scorekeeper for one sport, so testing is active here doesn't make sense.
        ScorekeeperFactory()
        scorekeeper = ScorekeeperFactory(user=self.user, sport=self.ice_hockey)
        ScorekeeperFactory(user=self.user, sport=self.baseball)
        scorekeepers = list(self.user.get_scorekeepers(self.ice_hockey))
        self.assertListEqual(scorekeepers, [scorekeeper])
