from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from ayrabo.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory
from sports.models import Sport
from sports.tests import SportFactory


# The models using the ActiveManager have tests...

class GenericChoiceManagerTests(BaseTestCase):
    def setUp(self):
        self.sport = SportFactory(name='Ice Hockey')
        self.league = LeagueFactory(full_name='Long Island Amateur Hockey League')

        self.choice1 = GenericChoiceFactory(content_object=self.sport, short_value='exhibition',
                                            long_value='Exhibition')
        self.choice2 = GenericChoiceFactory(content_object=self.sport, short_value='league', long_value='League')
        self.choice3 = GenericChoiceFactory(content_object=SportFactory())
        self.choice4 = GenericChoiceFactory(content_object=SportFactory())
        self.choice5 = GenericChoiceFactory(content_object=SportFactory())

        self.choice6 = GenericChoiceFactory(content_object=self.league)
        self.choice7 = GenericChoiceFactory(content_object=self.league)

    def test_get_choices_no_args(self):
        with self.assertRaisesMessage(ValueError, 'You must specify model_cls or instance'):
            GenericChoice.objects.get_choices()

    def test_get_choices_model_cls(self):
        # No choices for leagues should show up.
        choices = GenericChoice.objects.get_choices(model_cls=Sport)
        self.assertListEqual(list(choices), [self.choice1, self.choice2, self.choice3, self.choice4, self.choice5])

    def test_get_choices_instance(self):
        # No choices for leagues, or sports with a different pk should show up.
        choices = GenericChoice.objects.get_choices(instance=self.sport)
        self.assertListEqual(list(choices), [self.choice1, self.choice2])
