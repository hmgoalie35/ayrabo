from django.db import IntegrityError

from common.tests import GenericChoiceFactory
from ayrabo.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory


class GenericChoiceModelTests(BaseTestCase):
    def test_to_string(self):
        choice = GenericChoiceFactory(content_object=LeagueFactory(), short_value='model_choice_1',
                                      long_value='Model Choice 1')
        self.assertEqual(str(choice), 'Model Choice 1')

    def test_unique_together(self):
        league = LeagueFactory()
        choice = GenericChoiceFactory(content_object=league, short_value='model_choice_1',
                                      long_value='Model Choice 1')
        with self.assertRaises(IntegrityError):
            GenericChoiceFactory(content_type=choice.content_type, object_id=league.pk,
                                 short_value='model_choice_1',
                                 long_value='Model Choice 1')
