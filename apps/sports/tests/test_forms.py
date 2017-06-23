from escoresheet.utils.testing_utils import BaseTestCase
from sports.forms import SportRegistrationCreateForm
from sports.tests import SportFactory, SportRegistrationFactory
from accounts.tests import UserFactory


class SportRegistrationCreateFormTests(BaseTestCase):
    def setUp(self):
        self.user = UserFactory()
        self.hockey = SportFactory(name='Ice Hockey')
        self.soccer = SportFactory(name='Soccer')
        self.lax = SportFactory(name='Lacrosse')
        self.hockey_reg = SportRegistrationFactory(user=self.user, sport=self.hockey)
        self.soccer_reg = SportRegistrationFactory(user=self.user, sport=self.soccer)

        self.form_cls = SportRegistrationCreateForm

    def test_sets_fields_disabled(self):
        form = self.form_cls(sports_already_registered_for=[self.hockey.pk, self.soccer.pk])

        sport_field = form.fields['sport']
        qs = sport_field.queryset
        self.assertIn(self.lax, qs)
        self.assertNotIn(self.hockey, qs)
        self.assertNotIn(self.soccer_reg, qs)
