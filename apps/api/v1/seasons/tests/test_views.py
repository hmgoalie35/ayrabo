import datetime

from users.tests import UserFactory
from divisions.tests import DivisionFactory
from ayrabo.utils.testing import BaseAPITestCase
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from scorekeepers.tests import ScorekeeperFactory
from seasons.tests import SeasonFactory, HockeySeasonRosterFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


class SeasonRostersListAPIViewTests(BaseAPITestCase):
    url = 'v1:teams:season_rosters:list'

    def setUp(self):
        self.sport = SportFactory(id=1, name='Ice Hockey')
        self.league = LeagueFactory(sport=self.sport, full_name='Long Island Amateur Hockey League')
        self.division = DivisionFactory(name='Midget Minor AA', league=self.league)
        self.team = TeamFactory(id=1, name='Green Machine Icecats', division=self.division)
        self.season = SeasonFactory(id=1, league=self.league)
        self.formatted_url = self.format_url(pk=self.team.pk)

        self.user = UserFactory()

    # General
    def test_login_required(self):
        response = self.client.get(self.formatted_url)
        self.assertAPIError(response, 'unauthenticated')

    def test_manager_for_team_has_permission(self):
        SportRegistrationFactory(user=self.user, sport=self.sport, role='manager')
        ManagerFactory(user=self.user, team=self.team)
        self.client.force_login(self.user)
        response = self.client.get(self.formatted_url)
        self.assert_200(response)

    def test_scorekeeper_for_sport_has_permission(self):
        SportRegistrationFactory(user=self.user, sport=self.sport, role='scorekeeper')
        ScorekeeperFactory(user=self.user, sport=self.sport)
        self.client.force_login(self.user)
        response = self.client.get(self.formatted_url)
        self.assert_200(response)

    def test_manager_for_diff_team_permission_denied(self):
        SportRegistrationFactory(user=self.user, sport=self.sport, role='manager')
        ManagerFactory(user=self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.formatted_url)
        self.assertAPIError(response, 'permission_denied')

    def test_team_dne(self):
        SportRegistrationFactory(user=self.user, sport=self.sport, role='manager')
        ManagerFactory(user=self.user, team=self.team)
        self.client.force_login(self.user)
        response = self.client.get(self.format_url(pk=1000))
        self.assertAPIError(response, 'not_found')

    def test_sport_not_configured(self):
        team = TeamFactory(id=2, division__league__sport__name='Sport 1')
        SportRegistrationFactory(user=self.user, sport=self.sport, role='manager')
        ManagerFactory(user=self.user, team=team)
        self.client.force_login(self.user)
        response = self.client.get(self.format_url(pk=2))
        self.assertAPIError(response, 'sport_not_configured',
                            {'detail': 'Sport 1 is not currently configured.'})

    # List
    def test_get(self):
        SportRegistrationFactory(user=self.user, sport=self.sport, role='manager')
        ManagerFactory(user=self.user, team=self.team)
        self.client.force_login(self.user)
        HockeySeasonRosterFactory(id=1, name='Main Squad', season=self.season, team=self.team)
        HockeySeasonRosterFactory(id=2, name='Backup Squad', season=self.season, team=self.team)
        past_season = SeasonFactory(league=self.league, start_date=datetime.date(year=2016, month=9, day=23))
        HockeySeasonRosterFactory(id=3, name='Main Squad', season=past_season, team=self.team)
        HockeySeasonRosterFactory(id=4, name='Main Squad', season=self.season, team__division=self.division)
        response = self.client.get(self.formatted_url)
        data = [roster.get('id') for roster in response.data]
        self.assertListEqual(data, [1, 2, 3])

    def test_filter_by_season_id(self):
        SportRegistrationFactory(user=self.user, sport=self.sport, role='manager')
        ManagerFactory(user=self.user, team=self.team)
        self.client.force_login(self.user)

        HockeySeasonRosterFactory(id=1, name='Main Squad', season=self.season, team=self.team)
        HockeySeasonRosterFactory(id=2, name='Backup Squad', season=self.season, team=self.team)
        past_season = SeasonFactory(league=self.league, start_date=datetime.date(year=2016, month=9, day=23))
        HockeySeasonRosterFactory(id=3, name='Main Squad', season=past_season, team=self.team)
        response = self.client.get(self.formatted_url, data={'season': 1})
        data = [roster.get('id') for roster in response.data]
        self.assertListEqual(data, [1, 2])
