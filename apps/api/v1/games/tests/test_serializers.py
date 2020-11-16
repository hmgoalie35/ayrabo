import datetime
from unittest import mock

import pytz
from rest_framework import serializers

from api.exceptions import SportNotConfiguredAPIException
from api.v1.games.serializers import (
    AbstractGamePlayerCreateSerializer,
    HockeyGamePlayerBulkCreateSerializer,
    HockeyGamePlayerBulkDeleteSerializer, HockeyGamePlayerBulkUpdateSerializer, HockeyGamePlayerSerializer,
    validate_user_authorized_to_manage_team,
)
from ayrabo.utils.testing import BaseAPITestCase
from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from divisions.tests import DivisionFactory
from games.models import AbstractGame, HockeyGamePlayer
from games.tests import HockeyGameFactory, HockeyGamePlayerFactory
from leagues.tests import LeagueFactory
from players.tests import HockeyPlayerFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory


PERMISSION_DENIED_MSG = 'You do not have permission to manage game players for this team.'


class FixtureDataMixin:

    def _create_players(self, ids, team, sport):
        players = []
        for i in ids:
            players.append(HockeyPlayerFactory(id=i, team=team, sport=sport))
        return players

    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)

        self.home_team = TeamFactory(id=1, name='Green Machine IceCats', division=self.mm_aa)
        self.home_players = self._create_players([1, 2, 3, 4, 5], self.home_team, self.ice_hockey)
        HockeyPlayerFactory(id=11, team=self.home_team, is_active=False)
        self.away_team = TeamFactory(id=2, name='Aviator Gulls', division=self.mm_aa)
        self.away_players = self._create_players([6, 7, 8, 9, 10], self.away_team, self.ice_hockey)
        HockeyPlayerFactory(id=15, team=self.away_team, is_active=False)

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

        self.season_start = datetime.date(month=12, day=27, year=2017)
        self.season = SeasonFactory(league=self.liahl, start_date=self.season_start)

        self.start = datetime.datetime(month=12, day=27, year=2017, hour=19, minute=0)
        self.end = self.start + datetime.timedelta(hours=3)
        self.game = HockeyGameFactory(
            home_team=self.home_team,
            team=self.home_team,
            away_team=self.away_team,
            type=self.game_type,
            point_value=self.point_value,
            start=us_eastern.localize(self.start),
            end=us_eastern.localize(self.end),
            timezone=timezone,
            season=self.season,
            status=AbstractGame.SCHEDULED
        )


class ValidationUtilsTests(FixtureDataMixin, BaseAPITestCase):
    def test_validate_user_authorized_to_manage_team(self):
        with self.assertRaisesMessage(serializers.ValidationError, PERMISSION_DENIED_MSG):
            validate_user_authorized_to_manage_team(
                self.home_team,
                self.game,
                {'can_update_home_roster': False, 'can_update_away_roster': True}
            )

        with self.assertRaisesMessage(serializers.ValidationError, PERMISSION_DENIED_MSG):
            validate_user_authorized_to_manage_team(
                self.away_team,
                self.game,
                {'can_update_home_roster': True, 'can_update_away_roster': False}
            )

        with self.assertRaisesMessage(serializers.ValidationError, PERMISSION_DENIED_MSG):
            validate_user_authorized_to_manage_team(
                TeamFactory(id=222),
                self.game,
                {'can_update_home_roster': True, 'can_update_away_roster': True}
            )

        self.assertTrue(
            validate_user_authorized_to_manage_team(
                self.home_team,
                self.game,
                {'can_update_home_roster': True, 'can_update_away_roster': False}
            )
        )
        self.assertTrue(
            validate_user_authorized_to_manage_team(
                self.away_team,
                self.game,
                {'can_update_home_roster': True, 'can_update_away_roster': True}
            )
        )


class AbstractGamePlayerCreateSerializerTests(FixtureDataMixin, BaseAPITestCase):
    """Testing abstract class functionality via the `HockeyGamePlayerBulkCreateSerializer`"""

    def test_init(self):
        team1 = TeamFactory(id=3, division=self.mm_aa)
        team2 = TeamFactory(id=4, division=self.mm_aa)
        TeamFactory(id=5, division=self.mm_aa)
        TeamFactory(id=6, division=self.mm_aa)
        HockeyGameFactory(
            home_team=team1,
            team=team1,
            away_team=team2,
            type=self.game_type,
            point_value=self.point_value,
            season=self.season,
            status=AbstractGame.SCHEDULED
        )
        HockeyGameFactory(
            home_team=self.away_team,
            team=self.away_team,
            away_team=self.home_team,
            type=self.game_type,
            point_value=self.point_value,
            season=self.season,
            status=AbstractGame.SCHEDULED
        )
        HockeyPlayerFactory(id=12, team=team1, sport=self.ice_hockey)
        HockeyPlayerFactory(id=13, team=team2, sport=self.ice_hockey)

        # This is directly testing `get_game_model_cls`. Testing `get_player_model_cls` requires patching the dict
        # which seems like overkill.
        with self.assertRaisesMessage(SportNotConfiguredAPIException, 'Lax is not currently configured'):
            AbstractGamePlayerCreateSerializer(context={'sport': SportFactory(name='Lax')})

        s = HockeyGamePlayerBulkCreateSerializer(context={'sport': self.ice_hockey, 'game': self.game})
        # Make sure only home and away team
        self.assertEqual(list(s.fields['team'].queryset), [self.away_team, self.home_team])
        # Make sure only the game passed into context
        self.assertEqual(list(s.fields['game'].queryset), [self.game])
        # Make sure only active players from home or away team
        self.assertEqual(
            list(s.fields['player'].queryset.values_list('id', flat=True)),
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        )

    def test_validate(self):
        player1 = self.home_players[0]
        player2 = self.away_players[0]

        with self.assertRaisesMessage(serializers.ValidationError, PERMISSION_DENIED_MSG):
            s = HockeyGamePlayerBulkCreateSerializer(
                data={'team': self.home_team.id, 'game': self.game.id, 'player': player1.id},
                context={
                    'sport': self.ice_hockey,
                    'game': self.game,
                    'can_update_home_roster': False,
                    'can_update_away_roster': False
                }
            )
            s.is_valid(raise_exception=True)

        with self.assertRaisesMessage(serializers.ValidationError, 'Player does not belong to the specified team.'):
            s = HockeyGamePlayerBulkCreateSerializer(
                data={'team': self.home_team.id, 'game': self.game.id, 'player': player2.id},
                context={
                    'sport': self.ice_hockey,
                    'game': self.game,
                    'can_update_home_roster': True,
                    'can_update_away_roster': False
                }
            )
            s.is_valid(raise_exception=True)


class HockeyGamePlayerSerializerTests(FixtureDataMixin, BaseAPITestCase):
    def test_serializer(self):
        home_team_player = self.home_players[0]
        away_team_player = self.away_players[0]
        home_team_game_player = HockeyGamePlayerFactory(
            id=1,
            team=self.home_team,
            is_starting=True,
            game=self.game,
            player=home_team_player
        )
        away_team_game_player = HockeyGamePlayerFactory(
            id=2,
            team=self.away_team,
            is_starting=False,
            game=self.game,
            player=away_team_player
        )
        # Game players for both home and away teams
        s = HockeyGamePlayerSerializer([home_team_game_player, away_team_game_player], many=True)

        self.assertEqual(s.data, [
            {
                'id': 1,
                'team': self.home_team.id,
                'is_starting': True,
                'game': self.game.id,
                'player': home_team_player.id
            },
            {
                'id': 2,
                'team': self.away_team.id,
                'is_starting': False,
                'game': self.game.id,
                'player': away_team_player.id
            }
        ])


class HockeyGamePlayerBulkCreateSerializerTests(FixtureDataMixin, BaseAPITestCase):
    def test_bulk_create(self):
        context = {
            'sport': self.ice_hockey,
            'game': self.game,
            'can_update_home_roster': True,
            'can_update_away_roster': True
        }
        player1 = self.home_players[0]
        player2 = self.away_players[0]

        s = HockeyGamePlayerBulkCreateSerializer(
            data=[
                {'team': self.home_team.id, 'is_starting': True, 'game': self.game.id, 'player': player2.id},
                {'team': self.away_team.id, 'is_starting': False, 'game': self.game.id, 'player': player1.id},
            ],
            many=True,
            context=context
        )
        self.assertFalse(s.is_valid())

        s = HockeyGamePlayerBulkCreateSerializer(
            data=[
                {'team': self.home_team.id, 'is_starting': True, 'game': self.game.id, 'player': player1.id},
                {'team': self.away_team.id, 'is_starting': False, 'game': self.game.id, 'player': player2.id},
            ],
            many=True,
            context=context
        )
        s.is_valid(raise_exception=True)
        s.save()
        self.assertEqual(HockeyGamePlayer.objects.count(), 2)


class HockeyGamePlayerBulkUpdateSerializerTests(FixtureDataMixin, BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.home_team_player = self.home_players[0]
        self.away_team_player = self.away_players[0]
        self.home_team_game_player = HockeyGamePlayerFactory(
            id=1,
            team=self.home_team,
            is_starting=True,
            game=self.game,
            player=self.home_team_player
        )
        self.away_team_game_player = HockeyGamePlayerFactory(
            id=2,
            team=self.away_team,
            is_starting=True,
            game=self.game,
            player=self.away_team_player
        )
        mock_view = mock.Mock()
        mock_view.get_queryset.return_value = HockeyGamePlayer.objects.filter(
            id__in=[self.home_team_game_player.id, self.away_team_game_player.id]
        )
        self.context = {
            'view': mock_view,
            'sport': self.ice_hockey,
            'game': self.game,
            'can_update_home_roster': True,
            'can_update_away_roster': True
        }

    def test_validate(self):
        self.context.update({'can_update_home_roster': False, 'can_update_away_roster': False})
        s = HockeyGamePlayerBulkUpdateSerializer(
            data=[
                {'id': self.home_team_game_player.id, 'is_starting': False},
                {'id': self.away_team_game_player.id, 'is_starting': False},
            ],
            many=True,
            context=self.context
        )
        self.assertFalse(s.is_valid())

    def test_serializer(self):
        s = HockeyGamePlayerBulkUpdateSerializer(
            data=[
                {'id': self.home_team_game_player.id, 'is_starting': False, 'team': self.away_team.id},
                {'id': self.away_team_game_player.id, 'is_starting': False, 'team': self.home_team.id},
            ],
            many=True,
            context=self.context
        )
        s.is_valid()
        s.bulk_update()

        self.home_team_game_player.refresh_from_db()
        self.away_team_game_player.refresh_from_db()

        # Make sure user can't change the teams
        self.assertFalse(self.home_team_game_player.is_starting)
        self.assertEqual(self.home_team_game_player.team_id, self.home_team.id)
        self.assertFalse(self.away_team_game_player.is_starting)
        self.assertEqual(self.away_team_game_player.team_id, self.away_team.id)


class HockeyGamePlayerBulkDeleteSerializerTests(FixtureDataMixin, BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.home_team_player = self.home_players[0]
        self.away_team_player = self.away_players[0]
        self.home_team_game_player = HockeyGamePlayerFactory(
            id=1,
            team=self.home_team,
            is_starting=True,
            game=self.game,
            player=self.home_team_player
        )
        self.away_team_game_player = HockeyGamePlayerFactory(
            id=2,
            team=self.away_team,
            is_starting=True,
            game=self.game,
            player=self.away_team_player
        )
        mock_view = mock.Mock()
        mock_view.get_queryset.return_value = HockeyGamePlayer.objects.filter(
            id__in=[self.home_team_game_player.id, self.away_team_game_player.id]
        )
        self.context = {
            'view': mock_view,
            'sport': self.ice_hockey,
            'game': self.game,
            'can_update_home_roster': True,
            'can_update_away_roster': True
        }

    def test_validate(self):
        self.context.update({'can_update_home_roster': False, 'can_update_away_roster': False})
        s = HockeyGamePlayerBulkDeleteSerializer(
            data=[
                {'id': self.home_team_game_player.id},
                {'id': self.away_team_game_player.id},
            ],
            many=True,
            context=self.context
        )
        self.assertFalse(s.is_valid())

    def test_serializer(self):
        s = HockeyGamePlayerBulkDeleteSerializer(
            data=[
                {'id': self.home_team_game_player.id},
                {'id': self.away_team_game_player.id},
            ],
            many=True,
            context=self.context
        )
        s.is_valid()
        s.bulk_delete()

        self.assertEqual(HockeyGamePlayer.objects.count(), 0)
