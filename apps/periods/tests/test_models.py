from django.db import IntegrityError

from common.tests import GenericChoiceFactory
from escoresheet.utils.testing import BaseTestCase
from games.tests import HockeyGameFactory
from periods.tests import HockeyPeriodFactory
from sports.tests import SportFactory


class HockeyPeriodModelTests(BaseTestCase):
    def setUp(self):
        sport = SportFactory()
        self.point_value = GenericChoiceFactory(content_object=sport, short_value='1', long_value='1',
                                                type='game_point_value')
        self.type = GenericChoiceFactory(content_object=sport, short_value='exhibition', long_value='Exhibition',
                                         type='game_type')
        self.game = HockeyGameFactory(point_value=self.point_value, type=self.type)

    def test_name_game_unique_together(self):
        HockeyPeriodFactory(game=self.game, name='1')
        with self.assertRaises(IntegrityError):
            HockeyPeriodFactory(game=self.game, name='1')

    def test_to_str(self):
        self.assertEqual('1st', str(HockeyPeriodFactory(game=self.game, name='1')))
