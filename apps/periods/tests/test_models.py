from django.db import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from games.tests import HockeyGameFactory
from periods.tests import HockeyPeriodFactory
from sports.tests import SportFactory


class HockeyPeriodModelTests(BaseTestCase):
    def setUp(self):
        sport = SportFactory()
        self.point_value = GenericChoiceFactory(content_object=sport, short_value='1', long_value='1',
                                                type=GenericChoice.GAME_POINT_VALUE)
        self.type = GenericChoiceFactory(content_object=sport, short_value='exhibition', long_value='Exhibition',
                                         type=GenericChoice.GAME_TYPE)
        self.game = HockeyGameFactory(point_value=self.point_value, type=self.type)

    def test_name_game_unique_together(self):
        HockeyPeriodFactory(game=self.game, name='1')
        with self.assertRaises(IntegrityError):
            HockeyPeriodFactory(game=self.game, name='1')

    def test_to_str(self):
        self.assertEqual(str(HockeyPeriodFactory(game=self.game, name='1')), '1st')
