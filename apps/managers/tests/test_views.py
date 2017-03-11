from django.urls import reverse

from accounts.tests import UserFactory
from divisions.tests import DivisionFactory
from escoresheet.utils.testing_utils import BaseTestCase
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from managers.models import Manager
from managers.forms import ManagerForm
from managers.formset_helpers import ManagerFormSetHelper


class ManagerHomeViewTests(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super(ManagerHomeViewTests, cls).setUpClass()
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.liahl = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.mm_aa = DivisionFactory(name='Midget Minor AA', league=cls.liahl)
        cls.icecats = TeamFactory(name='Green Machine Icecats', division=cls.mm_aa)
        cls.season = SeasonFactory(league=cls.liahl)
        cls.baseball = SportFactory(name='Baseball')
        cls.mlb = LeagueFactory(full_name='Major League Baseball', sport=cls.baseball)
        cls.ale = DivisionFactory(name='American League East', league=cls.mlb)
        cls.yankees = TeamFactory(name='New York Yankees', division=cls.ale)

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)

        self.hockey_sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True, roles_mask=0)
        self.hockey_sr.set_roles(['Manager'])
        self.hockey_manager = ManagerFactory(user=self.user, team=self.icecats)

        self.baseball_sr = SportRegistrationFactory(user=self.user, sport=self.baseball, is_complete=True, roles_mask=0)
        self.baseball_sr.set_roles(['Manager'])
        self.baseball_manager = ManagerFactory(user=self.user, team=self.yankees)

        self.url = reverse('managers:home')
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous(self):
        self.client.logout()
        response = self.client.get(self.url)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'managers/manager_home.html')

    def test_get_redirects_if_no_manager_role(self):
        self.hockey_sr.set_roles(['Player', 'Coach'])
        self.baseball_sr.set_roles(['Referee'])

        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertHasMessage(response, 'You do not have permission to perform this action.')

    def test_context_dict_populated(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(list(context['teams']), [self.icecats, self.yankees])


class CreateManagersViewTests(BaseTestCase):
    def _format_url(self, role, **kwargs):
        return reverse(self.url.format(role=role), kwargs=kwargs)

    @classmethod
    def setUpClass(cls):
        super(CreateManagersViewTests, cls).setUpClass()
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.basketball = SportFactory(name='Basketball')

    def setUp(self):
        self.url = 'sportregistrations:{role}:create'
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.post_data = {
            'managers-TOTAL_FORMS': 1,
            'managers-INITIAL_FORMS': 0,
            'managers-MIN_NUM_FORMS': 1,
            'managers-MAX_NUM_FORMS': 10
        }

        self.user = UserFactory(email=self.email, password=self.password)

        self.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.division = DivisionFactory(name='Midget Minor AA', league=self.league)
        self.team = TeamFactory(name='Green Machine IceCats', division=self.division)

        self.sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=False)
        self.sr_2 = SportRegistrationFactory(user=self.user, sport=self.baseball, is_complete=False)
        self.sr.set_roles(['Manager'])
        self.client.login(email=self.email, password=self.password)

    def test_get_template_name(self):
        response = self.client.get(self._format_url('managers', pk=self.sr.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'managers/managers_create.html')

    def test_get_form_class(self):
        response = self.client.get(self._format_url('managers', pk=self.sr.id))
        form_cls = response.context['formset'].forms[0]
        self.assertIsInstance(form_cls, ManagerForm)

    def test_get_formset_prefix(self):
        response = self.client.get(self._format_url('managers', pk=self.sr.id))
        formset = response.context['formset']
        self.assertEqual(formset.prefix, 'managers')

    def test_get_model_class(self):
        response = self.client.get(self._format_url('managers', pk=self.sr.id))
        self.assertIs(response.context['formset'].model, Manager)

    def test_get_formset_helper_class(self):
        response = self.client.get(self._format_url('managers', pk=self.sr.id))
        self.assertIs(response.context['helper'], ManagerFormSetHelper)

    def test_get_role(self):
        response = self.client.get(self._format_url('managers', pk=self.sr.id))
        self.assertEqual(response.context['role'], 'Manager')

    def test_post_two_forms_same_team(self):
        form_data = {
            'managers-0-team': self.team.id,
            'managers-1-team': self.team.id,
            'managers-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('managers', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 1, 'team',
                                '{} has already been selected. Please choose another team or remove this form.'.format(
                                        self.team.name))
