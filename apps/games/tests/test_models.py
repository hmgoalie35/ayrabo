import datetime

import pytz
from django.core.exceptions import ValidationError

from common.tests import GenericChoiceFactory
from escoresheet.utils.testing import BaseTestCase
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
                                                type='game_point_value')
        self.game_type = GenericChoiceFactory(content_object=self.sport,
                                              short_value='exhibition',
                                              long_value='Exhibition',
                                              type='game_type')
        self.tz_name = 'America/New_York'
        home_team = TeamFactory(name='New York Islanders')
        away_team = TeamFactory(name='New York Rangers', division=home_team.division)
        # 12/16/2017 @ 07:00PM
        self.start = pytz.timezone('UTC').localize(datetime.datetime(year=2017, month=12, day=16, hour=19))
        self.game = HockeyGameFactory(type=self.game_type, point_value=self.point_value, start=self.start,
                                      timezone=self.tz_name, home_team=home_team, away_team=away_team)

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


class HockeyGoalModelTests(BaseTestCase):
    def setUp(self):
        self.sport = SportFactory(name='Ice Hockey')
        self.point_value = GenericChoiceFactory(content_object=self.sport,
                                                short_value='1',
                                                long_value='1',
                                                type='game_point_value')
        self.game_type = GenericChoiceFactory(content_object=self.sport,
                                              short_value='exhibition',
                                              long_value='Exhibition',
                                              type='game_type')
        home_team = TeamFactory(name='New York Islanders')
        away_team = TeamFactory(name='New York Rangers', division=home_team.division)
        self.start = pytz.timezone('UTC').localize(datetime.datetime(year=2017, month=12, day=16, hour=19))
        self.game = HockeyGameFactory(type=self.game_type, point_value=self.point_value, start=self.start,
                                      timezone='America/New_York', home_team=home_team, away_team=away_team)
        self.period = HockeyPeriodFactory(game=self.game, name='1')
        self.player = HockeyPlayerFactory(user__last_name='Tavares')
        self.time = datetime.timedelta(minutes=5, seconds=33)

    def test_to_string(self):
        goal = HockeyGoalFactory(game=self.game, period=self.period, player=self.player,
                                 time=self.time)
        self.assertEqual(str(goal), 'Tavares: 0:05:33')

    def test_clean_powerplay(self):
        with self.assertRaisesMessage(ValidationError, "{'penalty': ['This field is required for power play goals.']}"):
            HockeyGoalFactory(game=self.game, period=self.period, player=self.player, time=self.time, type='pp')

    def test_clean_shorthanded(self):
        msg = "{'penalty': ['This field is required for shorthanded goals.']}"
        with self.assertRaisesMessage(ValidationError, msg):
            HockeyGoalFactory(game=self.game, period=self.period, player=self.player, time=self.time, type='sh')


class HockeyAssistModelTests(BaseTestCase):
    pass
