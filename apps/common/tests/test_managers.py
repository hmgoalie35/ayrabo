from common.models import GenericModelChoice
from common.tests import GenericModelChoiceFactory
from escoresheet.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory
from sports.models import Sport
from sports.tests import SportFactory


# The models using the ActiveManager have tests...

class GenericModelChoiceManagerTests(BaseTestCase):
    def setUp(self):
        self.sport = SportFactory(name='Ice Hockey')
        self.league = LeagueFactory(full_name='Long Island Amateur Hockey League')

        self.choice1 = GenericModelChoiceFactory(content_object=self.sport, short_name='exhibition',
                                                 long_name='Exhibition')
        self.choice2 = GenericModelChoiceFactory(content_object=self.sport, short_name='league', long_name='League')
        self.choice3 = GenericModelChoiceFactory(content_object=SportFactory())
        self.choice4 = GenericModelChoiceFactory(content_object=SportFactory())
        self.choice5 = GenericModelChoiceFactory(content_object=SportFactory())

        self.choice6 = GenericModelChoiceFactory(content_object=self.league)
        self.choice7 = GenericModelChoiceFactory(content_object=self.league)

    def test_get_choices_no_args(self):
        with self.assertRaisesMessage(ValueError, 'You must specify model_cls or instance'):
            GenericModelChoice.objects.get_choices()

    def test_get_choices_model_cls(self):
        # No choices for leagues should show up.
        choices = GenericModelChoice.objects.get_choices(model_cls=Sport)
        self.assertListEqual(list(choices), [self.choice1, self.choice2, self.choice3, self.choice4, self.choice5])

    def test_get_choices_instance(self):
        # No choices for leagues, or sports with a different pk should show up.
        choices = GenericModelChoice.objects.get_choices(instance=self.sport)
        self.assertListEqual(list(choices), [self.choice1, self.choice2])
