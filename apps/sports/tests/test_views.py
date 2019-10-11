from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from coaches.tests import CoachFactory
from common.tests import WaffleSwitchFactory
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from players.tests import HockeyPlayerFactory
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class SportRegistrationCreateViewTests(BaseTestCase):
    url = 'sports:register'

    @classmethod
    def setUpTestData(cls):
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.basketball = SportFactory(name='Basketball')
        cls.league = LeagueFactory(name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.division = DivisionFactory(name='Midget Minor AA', league=cls.league)
        TeamFactory(name='Green Machine IceCats', division=cls.division)

    def setUp(self):
        self.sport_reg_switch = WaffleSwitchFactory(name='sport_registrations', active=True)
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.post_data = {
            'sportregistrations-TOTAL_FORMS': 1,
            'sportregistrations-INITIAL_FORMS': 0,
            'sportregistrations-MIN_NUM_FORMS': 1,
            'sportregistrations-MAX_NUM_FORMS': 3
        }

        self.user = UserFactory(email=self.email, password=self.password)
        self.login(email=self.email, password=self.password)

    # General
    def test_login_required(self):
        self.client.logout()
        url = self.format_url()
        self.assertLoginRequired(url)

    def test_has_permission_false(self):
        SportRegistrationFactory(sport=self.ice_hockey, user=self.user, role=SportRegistration.PLAYER)
        SportRegistrationFactory(sport=self.ice_hockey, user=self.user, role=SportRegistration.COACH)
        SportRegistrationFactory(sport=self.ice_hockey, user=self.user, role=SportRegistration.REFEREE)
        SportRegistrationFactory(sport=self.baseball, user=self.user, role=SportRegistration.COACH)
        SportRegistrationFactory(sport=self.basketball, user=self.user, role=SportRegistration.MANAGER)
        SportRegistrationFactory(sport=self.basketball, user=self.user, role=SportRegistration.SCOREKEEPER)
        response = self.client.get(self.format_url(), follow=True)
        self.assertHasMessage(response, 'You have already registered for all available sports.')
        self.assertRedirects(response, reverse('home'))

    def test_switch_inactive(self):
        self.sport_reg_switch.active = False
        self.sport_reg_switch.save()
        response = self.client.get(self.format_url())
        self.assert_404(response)

    # GET
    def test_get(self):
        response = self.client.get(self.format_url())
        context = response.context
        formset = context['formset']

        self.assertTemplateUsed(response, 'sports/sport_registration_create.html')
        self.assert_200(response)
        self.assertIsNotNone(formset.form)
        self.assertIsNotNone(formset)

    # POST
    def test_valid_post_one_form(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': [SportRegistration.PLAYER, SportRegistration.COACH]
        }
        self.post_data.update(form_data)
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        sport_registrations = SportRegistration.objects.filter(user=self.user, sport=self.ice_hockey)
        self.assertTrue(sport_registrations.filter(role='player').exists())
        self.assertTrue(sport_registrations.filter(role='coach').exists())
        self.assertRedirects(response, reverse('home'))
        self.assertHasMessage(response, 'You have been registered for Ice Hockey.')

    def test_valid_post_only_scorekeeper_role(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': [SportRegistration.SCOREKEEPER]
        }
        self.post_data.update(form_data)
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        # Sport registration should be marked as complete, redirect to home page
        sport_registrations = SportRegistration.objects.filter(user=self.user, sport=self.ice_hockey)
        scorekeeper_sport_reg = sport_registrations.filter(role=SportRegistration.SCOREKEEPER)
        self.assertTrue(scorekeeper_sport_reg.exists())
        self.assertTrue(scorekeeper_sport_reg.first().is_complete)
        self.assertRedirects(response, reverse('home'))
        self.assertHasMessage(response, 'You have been registered for Ice Hockey.')

    def test_valid_post_two_forms(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': [SportRegistration.PLAYER, SportRegistration.COACH,
                                           SportRegistration.SCOREKEEPER],
            'sportregistrations-1-sport': self.basketball.id,
            'sportregistrations-1-roles': [SportRegistration.PLAYER, SportRegistration.REFEREE]
        }
        self.post_data.update(form_data)
        self.post_data['sportregistrations-TOTAL_FORMS'] = 2

        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        sport_registrations = SportRegistration.objects.filter(user=self.user)
        self.assertTrue(sport_registrations.filter(sport=self.ice_hockey).count(), 3)
        self.assertTrue(sport_registrations.filter(sport=self.basketball).count(), 2)
        self.assertRedirects(response, reverse('home'))
        self.assertHasMessage(response, 'You have been registered for Ice Hockey, Basketball.')

    def test_valid_post_three_forms(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': [SportRegistration.PLAYER, SportRegistration.COACH],
            'sportregistrations-1-sport': self.basketball.id,
            'sportregistrations-1-roles': [SportRegistration.PLAYER, SportRegistration.REFEREE],
            'sportregistrations-2-sport': self.baseball.id,
            'sportregistrations-2-roles': [SportRegistration.MANAGER, SportRegistration.REFEREE]
        }
        self.post_data.update(form_data)
        self.post_data['sportregistrations-TOTAL_FORMS'] = 3

        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        sport_registrations = SportRegistration.objects.filter(user=self.user)
        self.assertTrue(sport_registrations.filter(sport=self.ice_hockey).count(), 2)
        self.assertTrue(sport_registrations.filter(sport=self.basketball).count(), 2)
        self.assertTrue(sport_registrations.filter(sport=self.baseball).count(), 2)
        self.assertRedirects(response, reverse('home'))
        self.assertHasMessage(response, 'You have been registered for Ice Hockey, Basketball, Baseball.')

    def test_post_two_forms_same_sport(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': [SportRegistration.REFEREE, SportRegistration.MANAGER],
            'sportregistrations-1-sport': self.ice_hockey.id,
            'sportregistrations-1-roles': [SportRegistration.PLAYER, SportRegistration.COACH]
        }
        self.post_data.update(form_data)
        self.post_data['sportregistrations-TOTAL_FORMS'] = 2
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 1, 'sport',
                                'Ice Hockey has already been selected. Choose another sport or remove this form.')

    def test_post_one_invalid_form(self):
        form_data = {
            'sportregistrations-0-sport': '',
        }
        self.post_data.update(form_data)
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'sport', 'This field is required.')
        self.assertFormsetError(response, 'formset', 0, 'roles', 'This field is required.')

    def test_post_two_invalid_forms(self):
        form_data = {
            'sportregistrations-0-sport': '',
            'sportregistrations-1-sport': '',
            'sportregistrations-1-roles': [SportRegistration.PLAYER],
        }
        self.post_data.update(form_data)
        self.post_data['sportregistrations-TOTAL_FORMS'] = 2
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'sport', 'This field is required.')
        self.assertFormsetError(response, 'formset', 1, 'sport', 'This field is required.')

    def test_post_empty_added_form(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': [SportRegistration.PLAYER, SportRegistration.COACH],
            'sportregistrations-1-sport': [''],
        }
        self.post_data.update(form_data)
        self.post_data['sportregistrations-TOTAL_FORMS'] = 2
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('home'))


class SportDashboardViewTests(BaseTestCase):
    url = 'sports:dashboard'

    def setUp(self):
        self.user = UserFactory(email='user@ayrabo.com', password='myweakpassword')
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)
        self.icecats = TeamFactory(name='Green Machine IceCats', division=self.mm_aa)
        self.baseball = SportFactory(name='Baseball')

    # General
    def test_login_required(self):
        url = self.format_url(slug='ice-hockey')
        self.assertLoginRequired(url)

    def test_sport_dne(self):
        self.login(user=self.user)
        response = self.client.get(self.format_url(slug='non-existent-sport'))
        self.assert_404(response)

    def test_no_sport_registrations_for_sport(self):
        self.login(user=self.user)
        response = self.client.get(self.format_url(slug='ice-hockey'))
        self.assert_404(response)

    # GET
    def test_get(self):
        sr_1 = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.PLAYER)
        sr_2 = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.COACH)
        HockeyPlayerFactory(user=self.user, sport=self.ice_hockey, team=self.icecats)
        CoachFactory(user=self.user, team=self.icecats)
        SportRegistrationFactory(user=self.user, sport=self.baseball, role=SportRegistration.COACH)

        self.login(user=self.user)

        response = self.client.get(self.format_url(slug='ice-hockey'))
        self.assert_200(response)
        self.assertTemplateUsed(response, 'sports/sport_dashboard.html')
        context = response.context
        sport_data = context.get('sport_data')
        sport_registrations = sport_data.get('registrations')
        roles = sport_data.get('roles')
        self.assertEqual(context.get('sport'), self.ice_hockey)
        self.assertEqual(sport_registrations, [sr_2, sr_1])
        self.assertEqual(list(roles.keys()), ['coach', 'player'])
        self.assertEqual(context.get('active_tab'), 'coach')
