from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from organizations.tests import OrganizationFactory
from scorekeepers.tests import ScorekeeperFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory
from users.authorizers import GameAuthorizer, SeasonRosterAuthorizer
from users.models import Permission
from users.tests import PermissionFactory, UserFactory


class GameAuthorizerTests(BaseTestCase):
    def setUp(self):
        self.sport = SportFactory()
        self.league = LeagueFactory(sport=self.sport)
        self.division = DivisionFactory(league=self.league)
        self.home_team_organization = OrganizationFactory(sport=self.sport)
        self.home_team = TeamFactory(division=self.division, organization=self.home_team_organization)
        self.away_team_organization = OrganizationFactory(sport=self.sport)
        self.away_team = TeamFactory(division=self.division, organization=self.away_team_organization)

        self.user1 = UserFactory()
        ManagerFactory(user=self.user1, team=self.home_team)

        self.user2 = UserFactory()
        PermissionFactory(user=self.user2, name=Permission.ADMIN, content_object=self.home_team_organization)

        self.user3 = UserFactory()
        ScorekeeperFactory(user=self.user3, sport=self.sport)

        self.user4 = UserFactory()
        ManagerFactory(user=self.user4, team=self.away_team)

    def test_can_user_create(self):
        self.assertTrue(GameAuthorizer(user=self.user1).can_user_create(self.home_team))
        self.assertTrue(GameAuthorizer(user=self.user2).can_user_create(self.home_team))
        self.assertFalse(GameAuthorizer(user=UserFactory()).can_user_create(self.home_team))

    def test_can_user_update(self):
        self.assertTrue(GameAuthorizer(user=self.user1).can_user_update(self.home_team))
        self.assertTrue(GameAuthorizer(user=self.user2).can_user_update(self.home_team))
        self.assertFalse(GameAuthorizer(user=UserFactory()).can_user_update(self.home_team))

    def test_can_user_update_game_roster(self):
        self.assertTrue(GameAuthorizer(user=self.user1).can_user_update_game_roster(self.home_team, self.sport))
        self.assertTrue(GameAuthorizer(user=self.user2).can_user_update_game_roster(self.home_team, self.sport))
        self.assertTrue(GameAuthorizer(user=self.user3).can_user_update_game_roster(self.home_team, self.sport))

        user = UserFactory()
        ManagerFactory(user=user, team=TeamFactory())
        self.assertFalse(GameAuthorizer(user=user).can_user_update_game_roster(self.home_team, self.sport))

    def test_can_user_update_game_rosters(self):
        self.assertTrue(GameAuthorizer(user=self.user1).can_user_update_game_rosters(
            self.home_team, self.away_team, self.sport)
        )
        self.assertTrue(GameAuthorizer(user=self.user2).can_user_update_game_rosters(
            self.home_team, self.away_team, self.sport)
        )
        self.assertTrue(GameAuthorizer(user=self.user3).can_user_update_game_rosters(
            self.home_team, self.away_team, self.sport)
        )
        self.assertTrue(GameAuthorizer(user=self.user4).can_user_update_game_rosters(
            self.home_team, self.away_team, self.sport)
        )

        user = UserFactory()
        ManagerFactory(user=user, team=TeamFactory())
        self.assertFalse(GameAuthorizer(user=user).can_user_update_game_rosters(
            self.home_team, self.away_team, self.sport)
        )


class SeasonRosterAuthorizerTests(BaseTestCase):
    def setUp(self):
        self.sport = SportFactory()
        self.league = LeagueFactory(sport=self.sport)
        self.division = DivisionFactory(league=self.league)
        self.organization = OrganizationFactory(sport=self.sport)
        self.team = TeamFactory(division=self.division, organization=self.organization)

        self.user1 = UserFactory()
        ManagerFactory(user=self.user1, team=self.team)

        self.user2 = UserFactory()
        PermissionFactory(user=self.user2, name=Permission.ADMIN, content_object=self.organization)

        self.user3 = UserFactory()
        ScorekeeperFactory(user=self.user3, sport=self.sport)

    def test_can_user_create(self):
        self.assertTrue(SeasonRosterAuthorizer(user=self.user1).can_user_create(team=self.team))
        self.assertTrue(SeasonRosterAuthorizer(user=self.user2).can_user_create(team=self.team))
        self.assertFalse(SeasonRosterAuthorizer(user=self.user3).can_user_create(team=self.team))

    def test_can_user_update(self):
        self.assertTrue(SeasonRosterAuthorizer(user=self.user1).can_user_update(team=self.team))
        self.assertTrue(SeasonRosterAuthorizer(user=self.user2).can_user_update(team=self.team))
        self.assertFalse(SeasonRosterAuthorizer(user=self.user3).can_user_update(team=self.team))
        self.assertFalse(SeasonRosterAuthorizer(user=UserFactory()).can_user_update(team=self.team))

    def test_can_user_list(self):
        self.assertTrue(SeasonRosterAuthorizer(user=self.user1).can_user_list(team=self.team, sport=self.sport))
        self.assertTrue(SeasonRosterAuthorizer(user=self.user2).can_user_list(team=self.team, sport=self.sport))
        self.assertTrue(SeasonRosterAuthorizer(user=self.user3).can_user_list(
            team=self.team, sport=self.sport, api=True)
        )
        self.assertFalse(SeasonRosterAuthorizer(user=self.user3).can_user_list(team=self.team, sport=self.sport))
