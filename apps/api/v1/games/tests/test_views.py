import datetime

import pytz
from rest_framework.reverse import reverse

from ayrabo.utils.testing import BaseAPITestCase
from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from divisions.tests import DivisionFactory
from games.models import HockeyGame, HockeyGamePlayer
from games.tests import HockeyGameFactory, HockeyGamePlayerFactory
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from players.tests import HockeyPlayerFactory
from scorekeepers.tests import ScorekeeperFactory
from seasons.tests import SeasonFactory
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class GamePlayerViewSetTests(BaseAPITestCase):
    def _get_list_url(self, sport_pk, game_pk):
        return reverse('v1:sports:games:players-list', kwargs={'pk': sport_pk, 'game_pk': game_pk})

    def _get_bulk_create_url(self, sport_pk, game_pk):
        return reverse('v1:sports:games:players-bulk-create', kwargs={'pk': sport_pk, 'game_pk': game_pk})

    def _get_bulk_update_url(self, sport_pk, game_pk):
        return reverse('v1:sports:games:players-bulk-update', kwargs={'pk': sport_pk, 'game_pk': game_pk})

    def _get_bulk_delete_url(self, sport_pk, game_pk):
        return reverse('v1:sports:games:players-bulk-delete', kwargs={'pk': sport_pk, 'game_pk': game_pk})

    def _create_game_players(self):
        self.home_game_player1 = HockeyGamePlayerFactory(
            game=self.game,
            team=self.home_team,
            player=self.home_player1,
            is_starting=True
        )
        self.home_game_player2 = HockeyGamePlayerFactory(
            game=self.game,
            team=self.home_team,
            player=self.home_player2
        )
        self.away_game_player1 = HockeyGamePlayerFactory(
            game=self.game,
            team=self.away_team,
            player=self.away_player1
        )

    def setUp(self):
        self.ice_hockey = SportFactory(id=1, name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)

        self.home_team = TeamFactory(id=1, name='Green Machine IceCats', division=self.mm_aa)
        self.home_player1 = HockeyPlayerFactory(id=1, team=self.home_team, sport=self.ice_hockey)
        self.home_player2 = HockeyPlayerFactory(id=2, team=self.home_team, sport=self.ice_hockey)
        self.away_team = TeamFactory(id=2, name='Aviator Gulls', division=self.mm_aa)
        self.away_player1 = HockeyPlayerFactory(id=3, team=self.away_team, sport=self.ice_hockey)

        self.game_type = GenericChoiceFactory(
            short_value='exhibition',
            long_value='Exhibition',
            type=GenericChoice.GAME_TYPE,
            content_object=self.ice_hockey
        )
        self.point_value = GenericChoiceFactory(
            short_value='2',
            long_value='2',
            type=GenericChoice.GAME_POINT_VALUE,
            content_object=self.ice_hockey
        )

        timezone = 'US/Eastern'
        us_eastern = pytz.timezone(timezone)

        now = datetime.datetime.now()
        season_start = now.date()
        self.season = SeasonFactory(league=self.liahl, start_date=season_start)

        start = now + datetime.timedelta(days=7)
        self.game = HockeyGameFactory(
            id=1,
            home_team=self.home_team,
            team=self.home_team,
            away_team=self.away_team,
            type=self.game_type,
            point_value=self.point_value,
            start=us_eastern.localize(start),
            end=us_eastern.localize(start + datetime.timedelta(hours=3)),
            timezone=timezone,
            season=self.season,
            status=HockeyGame.SCHEDULED
        )

        self.additional_team = TeamFactory(id=8, division=self.mm_aa)
        # Used to ensure get_queryset filters out records for other games
        start2 = now + datetime.timedelta(days=14)
        self.game2 = HockeyGameFactory(
            id=2,
            home_team=self.additional_team,
            team=self.additional_team,
            away_team=self.away_team,
            type=self.game_type,
            point_value=self.point_value,
            start=us_eastern.localize(start2),
            end=us_eastern.localize(start2 + datetime.timedelta(hours=2)),
            timezone=timezone,
            season=self.season,
            status=HockeyGame.SCHEDULED
        )
        HockeyGamePlayerFactory(
            id=55,
            game=self.game2,
            team=self.additional_team,
            player=HockeyPlayerFactory(id=4, team=self.additional_team, sport=self.ice_hockey)
        )
        HockeyGamePlayerFactory(
            id=54,
            game=self.game2,
            team=self.away_team,
            player=HockeyPlayerFactory(id=5, team=self.away_team, sport=self.ice_hockey)
        )

        self.user = UserFactory()
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.MANAGER)
        self.manager = ManagerFactory(user=self.user, team=self.home_team)

    def test_login_required(self):
        response = self.client.get(self._get_list_url(self.ice_hockey.pk, self.game.pk))
        self.assertAPIError(response, 'unauthenticated')

    def test_home_team_manager_allowed(self):
        self.login(user=self.user)

        response = self.client.get(self._get_list_url(self.ice_hockey.pk, self.game.pk))
        self.assert_200(response)

    def test_away_team_manager_allowed(self):
        user = UserFactory()
        SportRegistrationFactory(user=user, sport=self.ice_hockey, role=SportRegistration.MANAGER)
        ManagerFactory(user=user, team=self.away_team)
        self.login(user=user)

        response = self.client.get(self._get_list_url(self.ice_hockey.pk, self.game.pk))
        self.assert_200(response)

    def test_inactive_manager_forbidden(self):
        self.manager.is_active = False
        self.manager.save()
        self.login(user=self.user)

        response = self.client.get(self._get_list_url(self.ice_hockey.pk, self.game.pk))
        self.assertAPIError(response, 'permission_denied')

    def test_scorekeeper_allowed(self):
        user = UserFactory()
        SportRegistrationFactory(user=user, sport=self.ice_hockey, role=SportRegistration.SCOREKEEPER)
        ScorekeeperFactory(user=user, sport=self.ice_hockey)
        self.login(user=user)

        response = self.client.get(self._get_list_url(self.ice_hockey.pk, self.game.pk))
        self.assert_200(response)

    def test_inactive_scorekeeper_forbidden(self):
        user = UserFactory()
        SportRegistrationFactory(user=user, sport=self.ice_hockey, role=SportRegistration.SCOREKEEPER)
        ScorekeeperFactory(user=user, sport=self.ice_hockey, is_active=False)
        self.login(user=user)

        response = self.client.get(self._get_list_url(self.ice_hockey.pk, self.game.pk))
        self.assertAPIError(response, 'permission_denied')

    def test_scorekeeper_for_sport(self):
        user = UserFactory()
        sport = SportFactory(id=4)
        SportRegistrationFactory(user=user, sport=sport, role=SportRegistration.SCOREKEEPER)
        ScorekeeperFactory(user=user, sport=sport)
        self.login(user=user)

        response = self.client.get(self._get_list_url(self.ice_hockey.pk, self.game.pk))
        self.assertAPIError(response, 'permission_denied')

    def test_get_sport(self):
        self.login(user=self.user)

        # Sport DNE
        response = self.client.get(self._get_list_url(1000, self.game.pk))
        self.assertAPIError(response, 'not_found')

        # Sport exists
        response = self.client.get(self._get_list_url(self.ice_hockey.pk, self.game.pk))
        self.assert_200(response)

    def test_get_game(self):
        self.login(user=self.user)

        # Game DNE
        response = self.client.get(self._get_list_url(self.ice_hockey.pk, 1000))
        self.assertAPIError(response, 'not_found')

        # Game sport not configured
        cricket = SportFactory(id=2, name='Cricket')

        response = self.client.get(self._get_list_url(cricket.pk, self.game.pk))
        self.assertAPIError(
            response,
            'sport_not_configured',
            error_message_overrides={'detail': 'Cricket is not currently configured.'}
        )

        # Game exists
        response = self.client.get(self._get_list_url(self.ice_hockey.pk, self.game.pk))
        self.assert_200(response)

    def test_list(self):
        self._create_game_players()
        self.login(user=self.user)
        response = self.client.get(self._get_list_url(self.ice_hockey.pk, self.game.pk))

        self.assert_200(response)
        self.assertEqual(
            response.data,
            [
                {
                    'id': self.home_game_player1.pk,
                    'team': self.home_team.pk,
                    'is_starting': True,
                    'game': self.game.pk,
                    'player': self.home_player1.pk
                },
                {
                    'id': self.home_game_player2.pk,
                    'team': self.home_team.pk,
                    'is_starting': False,
                    'game': self.game.pk,
                    'player': self.home_player2.pk
                },
                {
                    'id': self.away_game_player1.pk,
                    'team': self.away_team.pk,
                    'is_starting': False,
                    'game': self.game.pk,
                    'player': self.away_player1.pk
                },
            ]
        )

    def test_bulk_create_valid(self):
        ScorekeeperFactory(user=self.user, sport=self.ice_hockey)
        self.login(user=self.user)
        response = self.client.post(self._get_bulk_create_url(self.ice_hockey.pk, self.game.pk), data=[
            {'team': self.home_team.pk, 'is_starting': True, 'game': self.game.pk, 'player': self.home_player1.pk},
            {'team': self.home_team.pk, 'is_starting': False, 'game': self.game.pk, 'player': self.home_player2.pk},
            {'team': self.away_team.pk, 'is_starting': True, 'game': self.game.pk, 'player': self.away_player1.pk},
        ])

        self.assert_201(response)
        self.assertEqual(HockeyGamePlayer.objects.filter(game=self.game).count(), 3)
        self.assertEqual(response.data, [
            {
                'id': 4,
                'team': self.home_team.pk,
                'is_starting': True,
                'game': self.game.pk,
                'player': self.home_player1.pk
            },
            {
                'id': 5,
                'team': self.home_team.pk,
                'is_starting': False,
                'game': self.game.pk,
                'player': self.home_player2.pk
            },
            {
                'id': 6,
                'team': self.away_team.pk,
                'is_starting': True,
                'game': self.game.pk,
                'player': self.away_player1.pk
            },
        ])

    def test_bulk_create_invalid(self):
        self.login(user=self.user)
        HockeyGamePlayerFactory(
            game=self.game,
            team=self.home_team,
            player=self.home_player1,
            is_starting=False
        )

        # Test unique constraint
        response = self.client.post(self._get_bulk_create_url(self.ice_hockey.pk, self.game.pk), data=[
            {},
            {'team': self.home_team.pk, 'is_starting': True, 'game': self.game.pk, 'player': self.home_player1.pk},
            {'team': self.away_team.pk, 'player': self.away_player1.pk},
        ])
        self.assertAPIError(response, 'validation_error', [
            {
                'team': ['This field is required.'],
                'game': ['This field is required.'],
                'player': ['This field is required.']
            },
            {'non_field_errors': ['The fields game, player must make a unique set.']},
            {'game': ['This field is required.']},
        ])

        # Test user doesn't have permission for team
        response = self.client.post(self._get_bulk_create_url(self.ice_hockey.pk, self.game.pk), data=[
            {'team': self.away_team.pk, 'is_starting': False, 'game': self.game.pk, 'player': self.away_player1.pk},
        ])
        self.assertAPIError(response, 'validation_error', [
            {'team': ['You do not have permission to manage game players for this team.']}
        ])

    def test_bulk_update_valid(self):
        self._create_game_players()
        self.login(user=self.user)

        response = self.client.post(self._get_bulk_update_url(self.ice_hockey.pk, self.game.pk), data=[
            {'id': self.home_game_player1.id, 'is_starting': False},
            {'id': self.home_game_player2.id, 'is_starting': True},
        ])
        self.assert_200(response)
        self.assertEqual(response.data, [
            {'id': self.home_game_player1.id, 'is_starting': False},
            {'id': self.home_game_player2.id, 'is_starting': True},
        ])
        self.home_game_player1.refresh_from_db()
        self.home_game_player2.refresh_from_db()
        self.assertFalse(self.home_game_player1.is_starting)
        self.assertTrue(self.home_game_player2.is_starting)

    def test_bulk_update_invalid(self):
        self._create_game_players()
        self.login(user=self.user)

        response = self.client.post(self._get_bulk_update_url(self.ice_hockey.pk, self.game.pk), data=[
            {},
            {'is_starting': False},
            {'id': self.away_game_player1.id, 'is_starting': True},
        ])
        self.assertAPIError(response, 'validation_error', [
            {'id': ['This field is required.']},
            {'id': ['This field is required.']},
            {'team': ['You do not have permission to manage game players for this team.']}
        ])

    def test_bulk_delete_valid(self):
        self._create_game_players()
        self.login(user=self.user)

        response = self.client.post(self._get_bulk_delete_url(self.ice_hockey.pk, self.game.pk), data=[
            {'id': self.home_game_player1.id},
            {'id': self.home_game_player2.id},
        ])
        self.assert_204(response)
        self.assertEqual(HockeyGamePlayer.objects.filter(game=self.game).count(), 1)

    def test_bulk_delete_invalid(self):
        self._create_game_players()
        self.login(user=self.user)

        response = self.client.post(self._get_bulk_delete_url(self.ice_hockey.pk, self.game.pk), data=[
            {},
            {'id': self.home_game_player1.id},
            {'id': self.home_game_player2.id},
            {'id': self.away_game_player1.id},
        ])
        self.assertAPIError(response, 'validation_error', [
            {'id': ['This field is required.']},
            {},
            {},
            {'team': ['You do not have permission to manage game players for this team.']}
        ])
        self.assertEqual(HockeyGamePlayer.objects.filter(game=self.game).count(), 3)
