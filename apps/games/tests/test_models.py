import datetime
from unittest import mock

import pytz
from django.core.exceptions import ValidationError
from django.utils import timezone

from ayrabo.utils.testing import BaseTestCase
from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from games.models import AbstractGame, HockeyGamePlayer, HockeyGoal
from games.tests import HockeyGameFactory, HockeyGamePlayerFactory, HockeyGoalFactory
from periods.models import HockeyPeriod
from periods.tests import HockeyPeriodFactory
from players.tests import HockeyPlayerFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory


class AbstractGameModelTests(BaseTestCase):
    """
    Testing this model via `HockeyGame`
    """

    def setUp(self):
        self.sport = SportFactory()
        self.point_value = GenericChoiceFactory(
            content_object=self.sport,
            short_value='1',
            long_value='1',
            type=GenericChoice.GAME_POINT_VALUE
        )
        self.game_type = GenericChoiceFactory(
            content_object=self.sport,
            short_value='exhibition',
            long_value='Exhibition',
            type=GenericChoice.GAME_TYPE
        )
        self.tz_name = 'US/Eastern'
        self.home_team = TeamFactory(name='New York Islanders')
        self.away_team = TeamFactory(name='New York Rangers', division=self.home_team.division)
        # 12/16/2017 @ 07:00PM
        self.start = pytz.utc.localize(datetime.datetime(year=2017, month=12, day=16, hour=19))
        self.game = HockeyGameFactory(
            status=AbstractGame.SCHEDULED,
            type=self.game_type,
            point_value=self.point_value,
            start=self.start,
            timezone=self.tz_name,
            home_team=self.home_team,
            away_team=self.away_team,
            period_duration=20,
        )

    def test_to_string(self):
        self.assertEqual(str(self.game), '12/16/2017 02:00 PM EST New York Islanders vs. New York Rangers')

    def test_datetime_localized(self):
        # 12/16/2017 @ 02:00PM
        expected = pytz.timezone(self.tz_name).localize(datetime.datetime(year=2017, month=12, day=16, hour=14))
        self.assertEqual(self.game.datetime_localized(self.game.start), expected)

    def test_datetime_formatted(self):
        self.assertEqual(self.game.datetime_formatted(self.game.start), '12/16/2017 02:00 PM EST')

    def test_init_periods(self):
        periods = self.game.init_periods()

        self.assertEqual(len(periods), 3)

        self.assertEqual(periods[0].duration, 20)
        self.assertEqual(periods[0].game, self.game)
        self.assertEqual(periods[0].name, '1')

        self.assertEqual(periods[1].duration, 20)
        self.assertEqual(periods[1].game, self.game)
        self.assertEqual(periods[1].name, '2')

        self.assertEqual(periods[2].duration, 20)
        self.assertEqual(periods[2].game, self.game)
        self.assertEqual(periods[2].name, '3')

        self.game.period_duration = 15
        self.game.save()

        periods = self.game.init_periods()

        self.assertEqual(len(periods), 3)
        self.assertEqual(periods[0].duration, 15)
        self.assertEqual(periods[0].game, self.game)
        self.assertEqual(periods[0].name, '1')

        self.assertEqual(periods[1].duration, 15)
        self.assertEqual(periods[1].game, self.game)
        self.assertEqual(periods[1].name, '2')

        self.assertEqual(periods[2].duration, 15)
        self.assertEqual(periods[2].game, self.game)
        self.assertEqual(periods[2].name, '3')

    def test_clean(self):
        """
        Django interprets datetimes in the currently active tz, therefore the start and end dates are localized to the
        same tz that is currently active (US/Eastern) to simulate this. The user, however wants the start and end time
        to be interpreted in US/Pacific, so the active tz needs to get removed, the resulting dt localized to US/Pacific
        and then stored in the db as UTC.

        12/26/2017 19:00 PST == 12/26/2017 22:00 EST == 12/27/2017 03:00 UTC
        """
        tz_pacific = 'US/Pacific'
        us_eastern = pytz.timezone(self.tz_name)
        # This is so making the dt naive works/simulates the tz from the user's profile being activated.
        timezone.activate(us_eastern)

        expected_start = pytz.utc.localize(datetime.datetime(month=12, day=27, year=2017, hour=3, minute=0))
        expected_end = pytz.utc.localize(datetime.datetime(month=12, day=27, year=2017, hour=6, minute=0))

        start = us_eastern.localize(datetime.datetime(month=12, day=26, year=2017, hour=19, minute=0))
        end = start + datetime.timedelta(hours=3)
        game = HockeyGameFactory(
            type=self.game_type,
            point_value=self.point_value,
            start=start,
            end=end,
            timezone=tz_pacific,
            home_team=self.home_team,
            away_team=self.away_team,
            period_duration=15,
        )
        game.full_clean()
        game.save()
        game.refresh_from_db()
        self.assertEqual(game.start, expected_start)
        self.assertEqual(game.end, expected_end)

    def test_is_in_progress(self):
        self.game.status = AbstractGame.IN_PROGRESS
        self.game.save()
        self.assertTrue(self.game.is_in_progress)

        self.game.status = AbstractGame.SCHEDULED
        self.game.save()
        self.assertFalse(self.game.is_in_progress)

    def test_is_completed(self):
        self.game.status = AbstractGame.COMPLETED
        self.game.save()
        self.assertTrue(self.game.is_completed)

        self.game.status = AbstractGame.SCHEDULED
        self.game.save()
        self.assertFalse(self.game.is_completed)

    def test_is_scheduled(self):
        self.game.status = AbstractGame.SCHEDULED
        self.game.save()
        self.assertTrue(self.game.is_scheduled)

        self.game.status = AbstractGame.CANCELLED
        self.game.save()
        self.assertFalse(self.game.is_scheduled)

    def test_is_postponed(self):
        self.game.status = AbstractGame.POSTPONED
        self.game.save()
        self.assertTrue(self.game.is_postponed)

        self.game.status = AbstractGame.CANCELLED
        self.game.save()
        self.assertFalse(self.game.is_postponed)

    def test_is_cancelled(self):
        self.game.status = AbstractGame.CANCELLED
        self.game.save()
        self.assertTrue(self.game.is_cancelled)

        self.game.status = AbstractGame.SCHEDULED
        self.game.save()
        self.assertFalse(self.game.is_cancelled)

    def test_can_update_true(self):
        self.game.status = AbstractGame.SCHEDULED
        self.game.end = timezone.now() + datetime.timedelta(hours=24)
        self.game.save()
        self.assertTrue(self.game.can_update())

    def test_can_update_invalid_status(self):
        self.game.status = AbstractGame.COMPLETED
        self.game.end = timezone.now() + datetime.timedelta(hours=24)
        self.game.save()
        self.assertFalse(self.game.can_update())

    def test_can_update_invalid_datetime(self):
        self.game.status = AbstractGame.SCHEDULED
        self.game.save()
        self.assertFalse(self.game.can_update())

    def test_can_initialize(self):
        self.game.status = AbstractGame.IN_PROGRESS
        self.game.save()
        self.assertFalse(self.game.can_initialize())

        self.game.status = AbstractGame.SCHEDULED
        self.game.save()
        self.assertTrue(self.game.can_initialize())

        self.game.start = timezone.now() + datetime.timedelta(days=30)
        self.game.end = self.game.start + datetime.timedelta(hours=2)
        self.game.save()
        self.assertFalse(self.game.can_initialize())

    @mock.patch('django.utils.timezone.now')
    def test_can_start_game(self, mock_tz_now):
        mock_tz_now.side_effect = [
            # Exactly 30 mins before
            datetime.datetime(month=12, day=16, year=2017, hour=18, minute=30, tzinfo=pytz.utc),
            # 15 mins after game start
            datetime.datetime(month=12, day=16, year=2017, hour=18, minute=45, tzinfo=pytz.utc),
            # 1 day before
            datetime.datetime(month=12, day=15, year=2017, hour=18, minute=0, tzinfo=pytz.utc),
        ]

        self.assertTrue(self.game.can_start_game())
        self.assertTrue(self.game.can_start_game())
        self.assertFalse(self.game.can_start_game())

    def test_init_game(self):
        self.game.init_game()

        self.game.refresh_from_db()

        self.assertEqual(self.game.status, AbstractGame.IN_PROGRESS)


class HockeyGameModelTests(BaseTestCase):
    def setUp(self):
        self.sport = SportFactory()
        self.point_value = GenericChoiceFactory(
            content_object=self.sport,
            short_value='1',
            long_value='1',
            type=GenericChoice.GAME_POINT_VALUE
        )
        self.game_type = GenericChoiceFactory(
            content_object=self.sport,
            short_value='exhibition',
            long_value='Exhibition',
            type=GenericChoice.GAME_TYPE
        )
        self.tz_name = 'US/Eastern'
        self.home_team = TeamFactory(name='New York Islanders')
        self.away_team = TeamFactory(name='New York Rangers', division=self.home_team.division)
        # 12/16/2017 @ 07:00PM
        self.start = pytz.utc.localize(datetime.datetime(year=2017, month=12, day=16, hour=19))
        self.game = HockeyGameFactory(
            type=self.game_type,
            point_value=self.point_value,
            start=self.start,
            timezone=self.tz_name,
            home_team=self.home_team,
            away_team=self.away_team
        )
        self.home_player1 = HockeyPlayerFactory(sport=self.sport, team=self.home_team, jersey_number='1')
        self.home_player2 = HockeyPlayerFactory(sport=self.sport, team=self.home_team, jersey_number='2')
        self.away_player1 = HockeyPlayerFactory(sport=self.sport, team=self.away_team, jersey_number='1')
        self.away_player2 = HockeyPlayerFactory(sport=self.sport, team=self.away_team, jersey_number='2')

        # Use to make sure _get_game_players filters by the current game
        HockeyGamePlayerFactory(game__type=self.game_type, game__point_value=self.point_value)

        self.home_hockey_game_player1 = HockeyGamePlayerFactory(
            team=self.home_team,
            game=self.game,
            player=self.home_player1
        )
        self.home_hockey_game_player2 = HockeyGamePlayerFactory(
            team=self.home_team,
            game=self.game,
            player=self.home_player2
        )
        self.away_hockey_game_player1 = HockeyGamePlayerFactory(
            team=self.away_team,
            game=self.game,
            player=self.away_player1
        )
        self.away_hockey_game_player2 = HockeyGamePlayerFactory(
            team=self.away_team,
            game=self.game,
            player=self.away_player2
        )

    def test_get_game_players(self):
        self.assertEqual(
            list(self.game._get_game_players(self.home_team.pk)),
            [self.home_hockey_game_player1, self.home_hockey_game_player2]
        )

    def test_home_team_game_players(self):
        self.assertEqual(
            list(self.game.home_team_game_players),
            [self.home_hockey_game_player1, self.home_hockey_game_player2]
        )

    def test_away_team_game_players(self):
        self.assertEqual(
            list(self.game.away_team_game_players),
            [self.away_hockey_game_player1, self.away_hockey_game_player2]
        )

    def test_delete_game_players(self):
        self.game.delete_game_players(self.home_team)
        qs = HockeyGamePlayer.objects.filter(game=self.game)
        self.assertEqual(qs.filter(team=self.home_team).count(), 0)
        # Make sure we only delete the home team game players
        self.assertEqual(qs.filter(team=self.away_team).count(), 2)


class HockeyGoalModelTests(BaseTestCase):
    def setUp(self):
        self.sport = SportFactory(name='Ice Hockey')
        self.point_value = GenericChoiceFactory(content_object=self.sport,
                                                short_value='1',
                                                long_value='1',
                                                type=GenericChoice.GAME_POINT_VALUE)
        self.game_type = GenericChoiceFactory(content_object=self.sport,
                                              short_value='exhibition',
                                              long_value='Exhibition',
                                              type=GenericChoice.GAME_TYPE)
        home_team = TeamFactory(name='New York Islanders')
        away_team = TeamFactory(name='New York Rangers', division=home_team.division)
        self.start = pytz.utc.localize(datetime.datetime(year=2017, month=12, day=16, hour=19))
        self.game = HockeyGameFactory(type=self.game_type, point_value=self.point_value, start=self.start,
                                      timezone='US/Eastern', home_team=home_team, away_team=away_team)
        self.period = HockeyPeriodFactory(game=self.game, name=HockeyPeriod.ONE)
        self.player = HockeyPlayerFactory(user__last_name='Tavares')
        self.time = datetime.timedelta(minutes=5, seconds=33)

    def test_to_string(self):
        goal = HockeyGoalFactory(game=self.game, period=self.period, player=self.player,
                                 time=self.time)
        self.assertEqual(str(goal), 'Tavares: 0:05:33')

    def test_clean_powerplay(self):
        with self.assertRaisesMessage(ValidationError, "{'penalty': ['This field is required for power play goals.']}"):
            HockeyGoalFactory(game=self.game, period=self.period, player=self.player, time=self.time,
                              type=HockeyGoal.POWER_PLAY)

    def test_clean_shorthanded(self):
        msg = "{'penalty': ['This field is required for shorthanded goals.']}"
        with self.assertRaisesMessage(ValidationError, msg):
            HockeyGoalFactory(game=self.game, period=self.period, player=self.player, time=self.time,
                              type=HockeyGoal.SHORTHANDED)


class HockeyAssistModelTests(BaseTestCase):
    pass
