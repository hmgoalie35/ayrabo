from django.db import IntegrityError

from common.tests import GenericModelChoiceFactory
from escoresheet.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory


class GenericModelChoiceModelTests(BaseTestCase):
    def test_to_string(self):
        choice = GenericModelChoiceFactory(content_object=LeagueFactory(), short_name='model_choice_1',
                                           long_name='Model Choice 1')
        self.assertEqual(str(choice), 'Model Choice 1')

    def test_unique_together(self):
        league = LeagueFactory()
        choice = GenericModelChoiceFactory(content_object=league, short_name='model_choice_1',
                                           long_name='Model Choice 1')
        with self.assertRaises(IntegrityError):
            GenericModelChoiceFactory(content_type=choice.content_type, object_id=league.pk,
                                      short_name='model_choice_1',
                                      long_name='Model Choice 1')
