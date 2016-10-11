from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.tests import UserFactory
from divisions.tests import DivisionFactory
from escoresheet.testing_utils import get_messages
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


class ManagerHomeViewTests(TestCase):
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

        self.url = reverse('manager:home')
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous(self):
        self.client.logout()
        response = self.client.get(self.url)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'managers/home.html')

    def test_get_redirects_if_no_manager_role(self):
        self.hockey_sr.set_roles(['Player', 'Coach'])
        self.baseball_sr.set_roles(['Referee'])

        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertIn('You do not have permission to perform this action.', get_messages(response))

    def test_context_dict_populated(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(list(context['teams']), [self.icecats, self.yankees])
