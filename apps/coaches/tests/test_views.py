from django.urls import reverse

from accounts.tests import UserFactory
from coaches.forms import CoachForm
from coaches.formset_helpers import CoachFormSetHelper
from coaches.models import Coach
from divisions.tests import DivisionFactory
from escoresheet.utils.testing_utils import BaseTestCase
from leagues.tests import LeagueFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


class CreateCoachesViewTests(BaseTestCase):
    def _format_url(self, role, **kwargs):
        return reverse(self.url.format(role=role), kwargs=kwargs)

    @classmethod
    def setUpClass(cls):
        super(CreateCoachesViewTests, cls).setUpClass()
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.basketball = SportFactory(name='Basketball')

    def setUp(self):
        self.url = 'sportregistrations:{role}:create'
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.post_data = {
            'coaches-TOTAL_FORMS': 1,
            'coaches-INITIAL_FORMS': 0,
            'coaches-MIN_NUM_FORMS': 1,
            'coaches-MAX_NUM_FORMS': 10
        }

        self.user = UserFactory(email=self.email, password=self.password)

        self.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.division = DivisionFactory(name='Midget Minor AA', league=self.league)
        self.team = TeamFactory(name='Green Machine IceCats', division=self.division)

        self.sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=False)
        self.sr_2 = SportRegistrationFactory(user=self.user, sport=self.baseball, is_complete=False)
        self.sr.set_roles(['Coach', 'Referee'])
        self.client.login(email=self.email, password=self.password)

    def test_get_template_name(self):
        response = self.client.get(self._format_url('coaches', pk=self.sr.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coaches/coaches_create.html')

    def test_get_form_class(self):
        response = self.client.get(self._format_url('coaches', pk=self.sr.id))
        form_cls = response.context['formset'].forms[0]
        self.assertIsInstance(form_cls, CoachForm)

    def test_get_formset_prefix(self):
        response = self.client.get(self._format_url('coaches', pk=self.sr.id))
        formset = response.context['formset']
        self.assertEqual(formset.prefix, 'coaches')

    def test_get_model_class(self):
        response = self.client.get(self._format_url('coaches', pk=self.sr.id))
        self.assertIs(response.context['formset'].model, Coach)

    def test_get_formset_helper_class(self):
        response = self.client.get(self._format_url('coaches', pk=self.sr.id))
        self.assertIs(response.context['helper'], CoachFormSetHelper)

    def test_get_role(self):
        response = self.client.get(self._format_url('coaches', pk=self.sr.id))
        self.assertEqual(response.context['role'], 'Coach')

    def test_post_two_forms_same_team(self):
        form_data = {
            'coaches-0-team': self.team.id,
            'coaches-0-position': "Head Coach",
            'coaches-1-team': self.team.id,
            'coaches-1-position': "Assistant Coach",
            'coaches-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('coaches', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 1, 'team',
                                '{} has already been selected. Please choose another team or remove this form.'.format(
                                        self.team.name))
