from ayrabo.utils.testing import BaseAPITestCase
from managers.tests import ManagerFactory
from players.tests import HockeyPlayerFactory
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class PlayersListAPIViewTests(BaseAPITestCase):
    url = 'v1:teams:players:list'

    def setUp(self):
        self.user = UserFactory()
        self.sport = SportFactory(name='Ice Hockey')
        self.team = TeamFactory(name='Green Machine IceCats', division__league__sport=self.sport)
        SportRegistrationFactory(user=self.user, sport=self.sport, role=SportRegistration.MANAGER)
        ManagerFactory(user=self.user, team=self.team)

        self.p1 = HockeyPlayerFactory(team=self.team, is_active=True)
        self.p2 = HockeyPlayerFactory(team=self.team, is_active=True)
        self.p3 = HockeyPlayerFactory(team=self.team, is_active=True)
        self.p4 = HockeyPlayerFactory(team=self.team, is_active=True)
        self.p5 = HockeyPlayerFactory(team=self.team, is_active=True)
        self.p6 = HockeyPlayerFactory(team=self.team, is_active=False)
        self.login(user=self.user)

    # General
    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.format_url(pk=self.team.pk))
        self.assertAPIError(response, 'unauthenticated')

    def test_filter_by_is_active(self):
        response = self.client.get(self.format_url(pk=self.team.pk), data={'is_active': True})
        data = [p.get('id') for p in response.data]
        self.assertListEqual(data, [self.p5.pk, self.p4.pk, self.p3.pk, self.p2.pk, self.p1.pk])

    def test_team_dne(self):
        response = self.client.get(self.format_url(pk=1000))
        self.assertAPIError(response, 'not_found')

    def test_sport_not_configured(self):
        team = TeamFactory(division__league__sport__name='Sport 1')
        response = self.client.get(self.format_url(pk=team.pk))
        self.assertAPIError(response, 'sport_not_configured',
                            error_message_overrides={'detail': 'Sport 1 is not currently configured.'})

    # List
    def test_list(self):
        # Make sure players are filtered by team
        team = TeamFactory(division__league__sport=self.sport)
        HockeyPlayerFactory(team=team, is_active=True)
        HockeyPlayerFactory(team=team, is_active=True)
        response = self.client.get(self.format_url(pk=self.team.pk))
        data = [p.get('id') for p in response.data]
        self.assertListEqual(data, [self.p6.pk, self.p5.pk, self.p4.pk, self.p3.pk, self.p2.pk, self.p1.pk])
