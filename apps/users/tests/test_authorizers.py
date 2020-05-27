from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from organizations.tests import OrganizationFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory
from users.authorizers import GameAuthorizer
from users.models import Permission
from users.tests import PermissionFactory, UserFactory


class GameAuthorizerTests(BaseTestCase):
    def test_can_user_create(self):
        sport = SportFactory()
        league = LeagueFactory(sport=sport)
        division = DivisionFactory(league=league)
        organization = OrganizationFactory(sport=sport)
        team = TeamFactory(division=division, organization=organization)

        user1 = UserFactory()
        ManagerFactory(user=user1, team=team)

        user2 = UserFactory()
        PermissionFactory(user=user2, name=Permission.ADMIN, content_object=organization)

        self.assertTrue(GameAuthorizer(user=user1).can_user_create(team))
        self.assertTrue(GameAuthorizer(user=user2).can_user_create(team))
        self.assertFalse(GameAuthorizer(user=UserFactory()).can_user_create(team))
