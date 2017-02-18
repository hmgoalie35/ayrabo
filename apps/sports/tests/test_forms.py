from escoresheet.utils.testing_utils import BaseTestCase
from sports.forms import CreateSportRegistrationForm
from sports.tests import SportFactory, SportRegistrationFactory
from accounts.tests import UserFactory


class CreateSportRegistrationFormTests(BaseTestCase):
    def setUp(self):
        self.user = UserFactory()
        self.hockey = SportFactory(name='Ice Hockey')
        self.soccer = SportFactory(name='Soccer')
        self.lax = SportFactory(name='Lacrosse')
        self.hockey_reg = SportRegistrationFactory(user=self.user, sport=self.hockey)
        self.soccer_reg = SportRegistrationFactory(user=self.user, sport=self.soccer)

        self.form_cls = CreateSportRegistrationForm

    def test_sets_fields_disabled(self):
        form = self.form_cls(sports_already_registered_for=[self.hockey_reg.id, self.soccer_reg.id])

        sport_field = form.fields['sport']
        qs = sport_field.queryset
        self.assertIn(self.lax, qs)
        self.assertNotIn(self.hockey, qs)
        self.assertNotIn(self.soccer_reg, qs)
