from django.urls import reverse

from accounts.tests import UserFactory
from divisions.tests import DivisionFactory
from escoresheet.utils.testing_utils import BaseTestCase
from leagues.tests import LeagueFactory
from referees.forms import RefereeForm
from referees.formset_helpers import RefereeFormSetHelper
from referees.models import Referee
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


class CreateRefereesViewTests(BaseTestCase):
    def _format_url(self, role, **kwargs):
        return reverse(self.url.format(role=role), kwargs=kwargs)

    @classmethod
    def setUpClass(cls):
        super(CreateRefereesViewTests, cls).setUpClass()
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.basketball = SportFactory(name='Basketball')

    def setUp(self):
        self.url = 'sportregistrations:{role}:create'
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.post_data = {
            'referees-TOTAL_FORMS': 1,
            'referees-INITIAL_FORMS': 0,
            'referees-MIN_NUM_FORMS': 1,
            'referees-MAX_NUM_FORMS': 10
        }

        self.user = UserFactory(email=self.email, password=self.password)

        self.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.division = DivisionFactory(name='Midget Minor AA', league=self.league)
        self.team = TeamFactory(name='Green Machine IceCats', division=self.division)

        self.sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=False)
        self.sr_2 = SportRegistrationFactory(user=self.user, sport=self.baseball, is_complete=False)
        self.sr.set_roles(['Referee'])
        self.client.login(email=self.email, password=self.password)

    def test_get_template_name(self):
        response = self.client.get(self._format_url('referees', pk=self.sr.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'referees/referees_create.html')

    def test_get_form_class(self):
        response = self.client.get(self._format_url('referees', pk=self.sr.id))
        form_cls = response.context['formset'].forms[0]
        self.assertIsInstance(form_cls, RefereeForm)

    def test_get_formset_prefix(self):
        response = self.client.get(self._format_url('referees', pk=self.sr.id))
        formset = response.context['formset']
        self.assertEqual(formset.prefix, 'referees')

    def test_get_model_class(self):
        response = self.client.get(self._format_url('referees', pk=self.sr.id))
        self.assertIs(response.context['formset'].model, Referee)

    def test_get_formset_helper_class(self):
        response = self.client.get(self._format_url('referees', pk=self.sr.id))
        self.assertIs(response.context['helper'], RefereeFormSetHelper)

    def test_get_role(self):
        response = self.client.get(self._format_url('referees', pk=self.sr.id))
        self.assertEqual(response.context['role'], 'Referee')

    def test_post_two_forms_same_league(self):
        form_data = {
            'referees-0-league': self.league.id,
            'referees-1-league': self.league.id,
            'referees-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('referees', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 1, 'league', '{} has already been selected. '
                                                                  'Please choose another league or remove this form.'
                                .format(self.league.full_name))
