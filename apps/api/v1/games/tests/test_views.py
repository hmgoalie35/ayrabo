import datetime

import pytz

from ayrabo.utils.testing import BaseAPITestCase
from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from divisions.tests import DivisionFactory
from games.models import HockeyGame
from games.tests import HockeyGameFactory
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from players.tests import HockeyPlayerFactory
from scorekeepers.tests import ScorekeeperFactory
from seasons.tests import SeasonFactory
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class GameRostersRetrieveUpdateAPIViewTests(BaseAPITestCase):
    url = 'v1:sports:games:rosters:retrieve-update'

    def _create_players(self, ids, team, sport):
        players = []
        for i in ids:
            players.append(HockeyPlayerFactory(id=i, team=team, sport=sport))
        return players

    # General
    def setUp(self):
        self.ice_hockey = SportFactory(id=1, name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)

        self.home_team = TeamFactory(id=1, name='Green Machine IceCats', division=self.mm_aa)
        self.home_players = self._create_players([1, 2, 3, 4, 5], self.home_team, self.ice_hockey)
        self.away_team = TeamFactory(id=2, name='Aviator Gulls', division=self.mm_aa)
        self.away_players = self._create_players([6, 7, 8, 9, 10], self.away_team, self.ice_hockey)

        self.game_type = GenericChoiceFactory(short_value='exhibition', long_value='Exhibition',
                                              type=GenericChoice.GAME_TYPE, content_object=self.ice_hockey)
        self.point_value = GenericChoiceFactory(short_value='2', long_value='2', type=GenericChoice.GAME_POINT_VALUE,
                                                content_object=self.ice_hockey)

        timezone = 'US/Eastern'
        us_eastern = pytz.timezone(timezone)

        self.season_start = datetime.date(month=12, day=27, year=2017)
        self.season = SeasonFactory(league=self.liahl, start_date=self.season_start)

        self.start = datetime.datetime(month=12, day=27, year=2017, hour=19, minute=0)
        self.end = self.start + datetime.timedelta(hours=3)
        self.game = HockeyGameFactory(id=1, home_team=self.home_team, team=self.home_team, away_team=self.away_team,
                                      type=self.game_type, point_value=self.point_value,
                                      start=us_eastern.localize(self.start), end=us_eastern.localize(self.end),
                                      timezone=timezone, season=self.season, status=HockeyGame.SCHEDULED)

        self.user = UserFactory()
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.MANAGER)
        self.manager = ManagerFactory(user=self.user, team=self.home_team)

    def test_login_required(self):
        response = self.client.get(self.format_url(pk=1, game_pk=1))
        self.assertAPIError(response, 'unauthenticated')

    def test_sport_dne(self):
        self.login(user=self.user)

        response = self.client.get(self.format_url(pk=1000, game_pk=1))
        self.assertAPIError(response, 'not_found')

    def test_sport_not_configured(self):
        self.login(user=self.user)
        SportFactory(id=2, name='Cricket')

        response = self.client.get(self.format_url(pk=2, game_pk=1))
        self.assertAPIError(response, 'sport_not_configured',
                            error_message_overrides={'detail': 'Cricket is not currently configured.'})

    def test_home_team_manager_allowed(self):
        self.login(user=self.user)

        response = self.client.get(self.format_url(pk=1, game_pk=1))
        self.assert_200(response)

    def test_away_team_manager_allowed(self):
        user = UserFactory()
        SportRegistrationFactory(user=user, sport=self.ice_hockey, role=SportRegistration.MANAGER)
        ManagerFactory(user=user, team=self.away_team)
        self.login(user=user)

        response = self.client.get(self.format_url(pk=1, game_pk=1))
        self.assert_200(response)

    def test_inactive_manager_forbidden(self):
        self.manager.is_active = False
        self.manager.save()
        self.login(user=self.user)

        response = self.client.get(self.format_url(pk=1, game_pk=1))
        self.assertAPIError(response, 'permission_denied')

    def test_scorekeeper_allowed(self):
        user = UserFactory()
        SportRegistrationFactory(user=user, sport=self.ice_hockey, role=SportRegistration.SCOREKEEPER)
        ScorekeeperFactory(user=user, sport=self.ice_hockey)
        self.login(user=user)

        response = self.client.get(self.format_url(pk=1, game_pk=1))
        self.assert_200(response)

    def test_inactive_scorekeeper_forbidden(self):
        user = UserFactory()
        SportRegistrationFactory(user=user, sport=self.ice_hockey, role=SportRegistration.SCOREKEEPER)
        ScorekeeperFactory(user=user, sport=self.ice_hockey, is_active=False)
        self.login(user=user)

        response = self.client.get(self.format_url(pk=1, game_pk=1))
        self.assertAPIError(response, 'permission_denied')

    def test_scorekeeper_for_sport(self):
        user = UserFactory()
        sport = SportFactory()
        SportRegistrationFactory(user=user, sport=sport, role=SportRegistration.SCOREKEEPER)
        ScorekeeperFactory(user=user, sport=sport)
        self.login(user=user)

        response = self.client.get(self.format_url(pk=1, game_pk=1))
        self.assertAPIError(response, 'permission_denied')

    # Retrieve
    def test_retrieve(self):
        self.game.home_players.add(self.home_players[0], self.home_players[1])
        self.game.away_players.add(self.away_players[0], self.away_players[1])
        self.login(user=self.user)

        response = self.client.get(self.format_url(pk=1, game_pk=1))
        home_players = response.data.get('home_players')
        away_players = response.data.get('away_players')
        self.assertListEqual(home_players, [1, 2])
        self.assertListEqual(away_players, [6, 7])

    # Update
    def test_patch(self):
        self.game.home_players.add(self.home_players[0], self.home_players[1])
        self.game.away_players.add(self.away_players[0], self.away_players[1])
        self.login(user=self.user)

        data = {
            'home_players': [1, 2, 3, 4],
        }
        response = self.client.patch(self.format_url(pk=1, game_pk=1), data=data)
        home_players = response.data.get('home_players')
        away_players = response.data.get('away_players')
        self.assertListEqual(home_players, [1, 2, 3, 4])
        self.assertListEqual(away_players, [6, 7])

    # There aren't tests for each possible case, I thought that was overkill. Those test cases should eventually be
    # added.
    def test_cant_update_home_roster(self):
        self.manager.is_active = False
        self.manager.save()
        ManagerFactory(user=self.user, team=self.away_team)
        self.login(user=self.user)
        data = {
            'home_players': [1, 2, 3, 4],
        }
        response = self.client.patch(self.format_url(pk=1, game_pk=1), data=data)
        self.assertAPIError(response, 'validation_error', {
            'home_players': ['You do not have permission to perform this action.']
        })

    def test_cant_update_away_roster(self):
        self.login(user=self.user)
        data = {
            'away_players': [6, 7],
        }
        response = self.client.patch(self.format_url(pk=1, game_pk=1), data=data)
        self.assertAPIError(response, 'validation_error', {
            'away_players': ['You do not have permission to perform this action.']
        })
