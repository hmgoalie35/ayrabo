import datetime

from django.db import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from games.tests import HockeyGameFactory
from penalties.tests import GenericPenaltyChoiceFactory, HockeyPenaltyFactory
from periods.models import HockeyPeriod
from periods.tests import HockeyPeriodFactory
from players.tests import HockeyPlayerFactory
from sports.tests import SportFactory


class GenericPenaltyChoiceModelTests(BaseTestCase):
    def setUp(self):
        self.sport = SportFactory()

    def test_unique_together(self):
        penalty_choice = GenericPenaltyChoiceFactory(content_object=self.sport, name='Interference')
        with self.assertRaises(IntegrityError):
            GenericPenaltyChoiceFactory(content_type=penalty_choice.content_type,
                                        object_id=penalty_choice.object_id,
                                        name='Interference')

    def test_to_string(self):
        penalty_choice = GenericPenaltyChoiceFactory(content_object=self.sport, name='Interference')
        self.assertEqual(str(penalty_choice), 'Interference')


class HockeyPenaltyModelTests(BaseTestCase):
    def test_to_string(self):
        sport = SportFactory()
        penalty_choice = GenericPenaltyChoiceFactory(content_object=sport, name='Interference')
        point_value = GenericChoiceFactory(content_object=sport,
                                           short_value='1',
                                           long_value='1',
                                           type=GenericChoice.GAME_POINT_VALUE)
        game_type = GenericChoiceFactory(content_object=sport,
                                         short_value='exhibition',
                                         long_value='Exhibition',
                                         type=GenericChoice.GAME_TYPE)
        player = HockeyPlayerFactory(user__first_name='Michael', user__last_name='Scott')
        game = HockeyGameFactory(point_value=point_value, type=game_type)
        period = HockeyPeriodFactory(game=game, name=HockeyPeriod.ONE)
        penalty = HockeyPenaltyFactory(game=game,
                                       player=player,
                                       duration=datetime.timedelta(minutes=2),
                                       type=penalty_choice,
                                       period=period)
        self.assertEqual(str(penalty), 'Scott: 0:02:00 Interference')
