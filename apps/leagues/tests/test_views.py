from ayrabo.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory
from sports.tests import SportFactory
from users.tests import UserFactory


class LeagueDetailViewTests(BaseTestCase):
    url = 'leagues:detail'

    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.user = UserFactory()

    def test_login_required(self):
        self.assertLoginRequired(self.format_url(slug=self.liahl.slug))

    # GET
    def test_get(self):
        self.login(user=self.user)
        response = self.client.get(self.format_url(slug=self.liahl.slug))
        context = response.context
        self.assert_200(response)
        self.assertTemplateUsed(response, 'leagues/league_detail.html')
        self.assertIsNotNone(context.get('league'))
