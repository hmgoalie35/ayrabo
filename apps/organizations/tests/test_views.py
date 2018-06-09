from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from organizations.tests import OrganizationFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import PermissionFactory, UserFactory


class OrganizationDetailViewTests(BaseTestCase):
    url = 'organizations:detail'

    def setUp(self):
        self.sport = SportFactory(name='Ice Hockey')
        self.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=self.sport)
        self.division = DivisionFactory(name='18U Milner', league=self.league)
        self.organization = OrganizationFactory(name='Green Machine IceCats')
        # Teams are in different divisions
        self.team1 = TeamFactory(division=self.division, organization=self.organization)
        self.team2 = TeamFactory(division__league=self.league, division__league__sport=self.sport,
                                 organization=self.organization)
        TeamFactory(division=self.division)

        self.user = UserFactory()
        SportRegistrationFactory(sport=self.sport, user=self.user)
        self.login(user=self.user)

    def test_login_required(self):
        self.client.logout()
        url = self.format_url(pk=self.organization.pk)
        response = self.client.get(url)
        self.assertRedirects(response, self.get_login_required_url(url))

    def test_has_permission(self):
        response = self.client.get(self.format_url(pk=self.organization.pk))
        self.assert_404(response)

    def test_get(self):
        PermissionFactory(user=self.user, name='admin', content_object=self.organization)
        user2 = UserFactory()
        PermissionFactory(user=user2, name='admin', content_object=self.organization)
        response = self.client.get(self.format_url(pk=self.organization.pk))

        self.assert_200(response)
        self.assertTemplateUsed('organizations/organization_detail.html')

        context = response.context
        active_tab = context.get('active_tab')
        teams = context.get('teams')
        organization_admins = context.get('organization_admins')
        support_email = context.get('support_email')

        self.assertEqual(active_tab, 'teams')
        self.assertListEqual(list(teams), [self.team1, self.team2])
        self.assertListEqual(list(organization_admins), [self.user, user2])
        self.assertEqual(support_email, 'harris@pittinsky.com')
