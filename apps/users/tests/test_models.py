from django.db import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from coaches.models import Coach
from coaches.tests import CoachFactory
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from managers.models import Manager
from managers.tests import ManagerFactory
from organizations.models import Organization
from organizations.tests import OrganizationFactory
from players.models import HockeyPlayer
from players.tests import HockeyPlayerFactory
from referees.models import Referee
from referees.tests import RefereeFactory
from scorekeepers.models import Scorekeeper
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

        self.player = HockeyPlayerFactory(user=self.user, sport=self.ice_hockey, team=self.team)
        self.coach = CoachFactory(user=self.user, team=self.team)
        self.referee = RefereeFactory(user=self.user, league=self.liahl)
        self.manager = ManagerFactory(user=self.user, team=self.team)
        self.scorekeeper = ScorekeeperFactory(user=self.user, sport=self.ice_hockey)
        # Sport reg for another user (should be excluded)
        SportRegistrationFactory()
        self.organization = OrganizationFactory(name='Long Beach Sharks', sport=self.ice_hockey)

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
        sr1 = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='coach')
        sr2 = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='player')
        sr3 = SportRegistrationFactory(user=self.user, sport=self.baseball, role='manager')

        result = self.user.sport_registration_data_by_sport()
        ice_hockey_data = result.get(self.ice_hockey)
        baseball_data = result.get(self.baseball)

        self.assertListEqual(list(result.keys()), [self.baseball, self.ice_hockey])
        self.assertListEqual(ice_hockey_data.get('registrations'), [sr1, sr2])
        self.assertListEqual(list(ice_hockey_data.get('roles').keys()), ['coach', 'player'])
        self.assertListEqual(baseball_data.get('registrations'), [sr3])
        self.assertListEqual(list(baseball_data.get('roles').keys()), ['manager'])

    def test_sport_registration_data_by_sport_no_registrations(self):
        result = self.user.sport_registration_data_by_sport()
        self.assertDictEqual(result, {})

    def test_sport_registration_data_by_sport_no_role_objects(self):
        Coach.objects.all().delete()
        sr1 = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='coach')

        result = self.user.sport_registration_data_by_sport()
        ice_hockey_data = result.get(self.ice_hockey)

        self.assertListEqual(list(result.keys()), [self.ice_hockey])
        self.assertListEqual(ice_hockey_data.get('registrations'), [sr1])
        self.assertListEqual(list(ice_hockey_data.get('roles').get('coach')), [])

    def test_get_roles(self):
        sr1 = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='coach')
        sr2 = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='player')
        sr3 = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='referee')
        sr4 = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='manager')
        sr5 = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role='scorekeeper')
        PermissionFactory(user=self.user, name='admin', content_object=self.organization)

        result = self.user.get_roles(self.ice_hockey, [sr1, sr2, sr3, sr4, sr5])

        self.assertListEqual(list(result.get('coach')), list(Coach.objects.filter(user=self.user)))
        self.assertListEqual(list(result.get('manager')), list(Manager.objects.filter(user=self.user)))
        self.assertListEqual(list(result.get('player')), list(HockeyPlayer.objects.filter(user=self.user)))
        self.assertListEqual(list(result.get('referee')), list(Referee.objects.filter(user=self.user)))
        self.assertListEqual(list(result.get('scorekeeper')), list(Scorekeeper.objects.filter(user=self.user)))
        self.assertListEqual(list(result.get('organization')),
                             list(Organization.objects.filter(name='Long Beach Sharks')))

    def test_get_players(self):
        HockeyPlayerFactory(sport=self.ice_hockey, team=self.team)
        team = TeamFactory(division__league__sport=self.ice_hockey)
        HockeyPlayerFactory(user=self.user, sport=self.ice_hockey, team=team, is_active=False)
        players = self.user.get_players(self.ice_hockey)
        self.assertListEqual(list(players), [self.player])

    def test_get_players_sport_not_configured(self):
        players = self.user.get_players(SportFactory(name='Invalid Sport'))
        self.assertListEqual(players, [])

    def test_get_coaches(self):
        CoachFactory(team=self.team)
        CoachFactory(user=self.user, team=TeamFactory(division__league__sport=self.baseball))
        CoachFactory(user=self.user, team=TeamFactory(division__league__sport=self.ice_hockey), is_active=False)
        coaches = self.user.get_coaches(self.ice_hockey)
        self.assertListEqual(list(coaches), [self.coach])

    def test_get_referees(self):
        RefereeFactory(league=self.liahl)
        RefereeFactory(user=self.user, league=LeagueFactory(sport=self.baseball))
        RefereeFactory(user=self.user, league=LeagueFactory(sport=self.ice_hockey), is_active=False)
        referees = self.user.get_referees(self.ice_hockey)
        self.assertListEqual(list(referees), [self.referee])

    def test_get_managers(self):
        ManagerFactory(team=self.team)
        ManagerFactory(user=self.user, team=TeamFactory(division__league__sport=self.baseball))
        ManagerFactory(user=self.user, team=TeamFactory(division__league__sport=self.ice_hockey), is_active=False)
        managers = list(self.user.get_managers(self.ice_hockey))
        self.assertListEqual(managers, [self.manager])

    def test_get_scorekeepers(self):
        # Users can only be registered as a scorekeeper for one sport, so testing is active here doesn't make sense.
        ScorekeeperFactory()
        ScorekeeperFactory(user=self.user, sport=self.baseball)
        scorekeepers = list(self.user.get_scorekeepers(self.ice_hockey))
        self.assertListEqual(scorekeepers, [self.scorekeeper])
