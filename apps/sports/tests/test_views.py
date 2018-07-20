from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
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
        cls.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.division = DivisionFactory(name='Midget Minor AA', league=cls.league)
        TeamFactory(name='Green Machine IceCats', division=cls.division)

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.post_data = {
            'sportregistrations-TOTAL_FORMS': 1,
            'sportregistrations-INITIAL_FORMS': 0,
            'sportregistrations-MIN_NUM_FORMS': 1,
            'sportregistrations-MAX_NUM_FORMS': 3
        }

        self.user = UserFactory(email=self.email, password=self.password)
        self.client.login(email=self.email, password=self.password)

    # General
    def test_login_required(self):
        self.client.logout()
        url = self.format_url()
        response = self.client.get(url)
        self.assertRedirects(response, self.get_login_required_url(url))

    def test_has_permission_false(self):
        SportRegistrationFactory(sport=self.ice_hockey, user=self.user, role='player')
        SportRegistrationFactory(sport=self.baseball, user=self.user, role='coach')
        SportRegistrationFactory(sport=self.basketball, user=self.user, role='manager')
        response = self.client.get(self.format_url(), follow=True)
        self.assertHasMessage(response, 'You have already registered for all available sports.')
        self.assertRedirects(response, reverse('home'))

    # GET
    def test_get(self):
        response = self.client.get(self.format_url())
        context = response.context

        self.assertTemplateUsed(response, 'sports/sport_registration_create.html')
        self.assert_200(response)
        # TODO Make sure correct form, formset, etc were used
        self.assertIsNotNone(context['formset'])

    # POST
    def test_valid_post_one_form(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': ['player', 'coach']
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
            'sportregistrations-0-roles': ['scorekeeper']
        }
        self.post_data.update(form_data)
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        # Sport registration should be marked as complete, redirect to home page
        sport_registrations = SportRegistration.objects.filter(user=self.user, sport=self.ice_hockey)
        scorekeeper_sport_reg = sport_registrations.filter(role='scorekeeper')
        self.assertTrue(scorekeeper_sport_reg.exists())
        self.assertTrue(scorekeeper_sport_reg.first().is_complete)
        self.assertRedirects(response, reverse('home'))
        self.assertHasMessage(response, 'You have been registered for Ice Hockey.')

    def test_valid_post_two_forms(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': ['player', 'coach', 'scorekeeper'],
            'sportregistrations-1-sport': self.basketball.id,
            'sportregistrations-1-roles': ['player', 'referee']
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
            'sportregistrations-0-roles': ['player', 'coach'],
            'sportregistrations-1-sport': self.basketball.id,
            'sportregistrations-1-roles': ['player', 'referee'],
            'sportregistrations-2-sport': self.baseball.id,
            'sportregistrations-2-roles': ['manager', 'referee']
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
            'sportregistrations-0-roles': ['referee', 'manager'],
            'sportregistrations-1-sport': self.ice_hockey.id,
            'sportregistrations-1-roles': ['player', 'coach']
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
            'sportregistrations-1-roles': ['player'],
        }
        self.post_data.update(form_data)
        self.post_data['sportregistrations-TOTAL_FORMS'] = 2
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'sport', 'This field is required.')
        self.assertFormsetError(response, 'formset', 1, 'sport', 'This field is required.')

    def test_post_empty_added_form(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': ['player', 'coach'],
            'sportregistrations-1-sport': [''],
        }
        self.post_data.update(form_data)
        self.post_data['sportregistrations-TOTAL_FORMS'] = 2
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('home'))
