import datetime

import pytz
from django.core.exceptions import ValidationError
from django.utils import timezone

from ayrabo.utils.testing import BaseTestCase
from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from games.models import AbstractGame, HockeyGoal
from games.tests import HockeyGameFactory, HockeyGoalFactory
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
        self.point_value = GenericChoiceFactory(content_object=self.sport,
                                                short_value='1',
                                                long_value='1',
                                                type=GenericChoice.GAME_POINT_VALUE)
        self.game_type = GenericChoiceFactory(content_object=self.sport,
                                              short_value='exhibition',
                                              long_value='Exhibition',
                                              type=GenericChoice.GAME_TYPE)
        self.tz_name = 'US/Eastern'
        self.home_team = TeamFactory(name='New York Islanders')
        self.away_team = TeamFactory(name='New York Rangers', division=self.home_team.division)
        # 12/16/2017 @ 07:00PM
        self.start = pytz.utc.localize(datetime.datetime(year=2017, month=12, day=16, hour=19))
        self.game = HockeyGameFactory(type=self.game_type, point_value=self.point_value, start=self.start,
                                      timezone=self.tz_name, home_team=self.home_team, away_team=self.away_team)

    def test_to_string(self):
        self.assertEqual(str(self.game), '12/16/2017 02:00 PM EST New York Islanders vs. New York Rangers')

    def test_datetime_localized(self):
        # 12/16/2017 @ 02:00PM
        expected = pytz.timezone(self.tz_name).localize(datetime.datetime(year=2017, month=12, day=16, hour=14))
        self.assertEqual(self.game.datetime_localized(self.game.start), expected)

    def test_datetime_formatted(self):
        self.assertEqual(self.game.datetime_formatted(self.game.start), '12/16/2017 02:00 PM EST')

    def test_init_periods(self):
        self.game.init_periods(datetime.timedelta(minutes=20))
        periods = HockeyPeriod.objects.filter(game=self.game).values_list('name', flat=True)
        self.assertListEqual(list(periods), ['1', '2', '3', 'ot1'])

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
        game = HockeyGameFactory(type=self.game_type, point_value=self.point_value, start=start, end=end,
                                 timezone=tz_pacific,
                                 home_team=self.home_team, away_team=self.away_team)
        game.full_clean()
        game.save()
        game.refresh_from_db()
        self.assertEqual(game.start, expected_start)
        self.assertEqual(game.end, expected_end)

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
