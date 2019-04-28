from ayrabo.utils.testing import BaseAPITestCase
from managers.tests import ManagerFactory
from players.tests import HockeyPlayerFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class PlayersListAPIViewTests(BaseAPITestCase):
    url = 'v1:teams:players:list'

    def setUp(self):
        self.user = UserFactory()
        self.sport = SportFactory(name='Ice Hockey')
        team = TeamFactory(id=1, name='Green Machine IceCats', division__league__sport=self.sport)
        SportRegistrationFactory(user=self.user, sport=self.sport, role='manager')
        ManagerFactory(user=self.user, team=team)

        HockeyPlayerFactory(id=1, team=team, is_active=True)
        HockeyPlayerFactory(id=2, team=team, is_active=True)
        HockeyPlayerFactory(id=3, team=team, is_active=True)
        HockeyPlayerFactory(id=4, team=team, is_active=True)
        HockeyPlayerFactory(id=5, team=team, is_active=True)
        HockeyPlayerFactory(id=6, team=team, is_active=False)
        self.login(user=self.user)

    # General
    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.format_url(pk=1))
        self.assertAPIError(response, 'unauthenticated')

    def test_filter_by_is_active(self):
        response = self.client.get(self.format_url(pk=1), data={'is_active': True})
        data = [p.get('id') for p in response.data]
        self.assertListEqual(data, [1, 2, 3, 4, 5])

    def test_team_dne(self):
        response = self.client.get(self.format_url(pk=1000))
        self.assertAPIError(response, 'not_found')

    def test_sport_not_configured(self):
        TeamFactory(id=2, division__league__sport__name='Sport 1')
        response = self.client.get(self.format_url(pk=2))
        self.assertAPIError(response, 'sport_not_configured',
                            error_message_overrides={'detail': 'Sport 1 is not currently configured.'})

    # List
    def test_list(self):
        # Make sure players are filtered by team
        team = TeamFactory(division__league__sport=self.sport)
        HockeyPlayerFactory(team=team, is_active=True)
        HockeyPlayerFactory(team=team, is_active=True)
        response = self.client.get(self.format_url(pk=1))
        data = [p.get('id') for p in response.data]
        self.assertListEqual(data, [1, 2, 3, 4, 5, 6])
