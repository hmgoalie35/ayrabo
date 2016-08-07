from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.tests.factories.UserFactory import UserFactory
from escoresheet.testing_utils import get_messages
from sports.models import SportRegistration
from sports.tests.factories.SportFactory import SportFactory
from sports.tests.factories.SportRegistrationFactory import SportRegistrationFactory


class CreateSportRegistrationViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(CreateSportRegistrationViewTests, cls).setUpClass()
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.basketball = SportFactory(name='Basketball')

    def setUp(self):
        self.url = reverse('sport:create_sport_registration')
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.post_data = {
            'sportregistration_set-TOTAL_FORMS': 1,
            'sportregistration_set-INITIAL_FORMS': 0,
            'sportregistration_set-MIN_NUM_FORMS': 1,
            'sportregistration_set-MAX_NUM_FORMS': 3
        }

        self.user = UserFactory(email=self.email, password=self.password)
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_renders_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'sports/sport_registration_create.html')

    def test_200_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_redirects_already_registered_for_all_sports(self):
        SportRegistrationFactory(sport=self.ice_hockey, user=self.user, is_complete=False)
        SportRegistrationFactory(sport=self.baseball, user=self.user, is_complete=False)
        SportRegistrationFactory(sport=self.basketball, user=self.user, is_complete=False)
        response = self.client.get(self.url, follow=True)
        self.assertIn(
                'You have already registered for all available sports. Check back later to see if any new sports have been added.',
                get_messages(response))
        self.assertRedirects(response, reverse('home'))

    def test_form_only_displays_sports_not_registered_for(self):
        SportRegistrationFactory(sport=self.ice_hockey, user=self.user, is_complete=False)
        response = self.client.get(self.url)
        formset_as_html = response.context['formset'].as_p()
        self.assertNotIn('Ice Hockey', formset_as_html)
        self.assertIn('Basketball', formset_as_html)
        self.assertIn('Baseball', formset_as_html)

    def test_context_populated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['remaining_sport_count'], 3)
        self.assertFalse(response.context['user_registered_for_all_sports'])
        self.assertIsNotNone(response.context['formset'])

    # POST
    def test_post_anonymous_user(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.post_data, follow=True)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_post_redirects_already_registered_for_all_sports(self):
        SportRegistrationFactory(sport=self.ice_hockey, user=self.user, is_complete=False)
        SportRegistrationFactory(sport=self.baseball, user=self.user, is_complete=False)
        SportRegistrationFactory(sport=self.basketball, user=self.user, is_complete=False)
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertIn(
                'You have already registered for all available sports. Check back later to see if any new sports have been added.',
                get_messages(response))
        self.assertRedirects(response, reverse('home'))

    def test_valid_post_one_form(self):
        form_data = {
            'sportregistration_set-0-sport': self.ice_hockey.id,
            'sportregistration_set-0-roles': ['Player', 'Coach']
        }
        self.post_data.update(form_data)
        response = self.client.post(self.url, data=self.post_data, follow=True)
        sr = SportRegistration.objects.filter(user=self.user, sport=self.ice_hockey)
        self.assertTrue(sr.exists())
        self.assertEqual(sr.first().roles, ['Player', 'Coach'])
        self.assertRedirects(response, reverse('sport:finish_sport_registration'))

    def test_valid_post_two_forms(self):
        form_data = {
            'sportregistration_set-0-sport': self.ice_hockey.id,
            'sportregistration_set-0-roles': ['Player', 'Coach'],
            'sportregistration_set-1-sport': self.basketball.id,
            'sportregistration_set-1-roles': ['Player', 'Referee']
        }
        self.post_data.update(form_data)
        self.post_data['sportregistration_set-TOTAL_FORMS'] = 2

        response = self.client.post(self.url, data=self.post_data, follow=True)
        sr = SportRegistration.objects.filter(user=self.user)
        self.assertEqual(sr.count(), 2)
        self.assertEqual(sr[0].roles, ['Player', 'Coach'])
        self.assertEqual(sr[1].roles, ['Player', 'Referee'])
        self.assertRedirects(response, reverse('sport:finish_sport_registration'))

    def test_valid_post_three_forms(self):
        form_data = {
            'sportregistration_set-0-sport': self.ice_hockey.id,
            'sportregistration_set-0-roles': ['Player', 'Coach'],
            'sportregistration_set-1-sport': self.basketball.id,
            'sportregistration_set-1-roles': ['Player', 'Referee'],
            'sportregistration_set-2-sport': self.baseball.id,
            'sportregistration_set-2-roles': ['Manager', 'Referee']
        }
        self.post_data.update(form_data)
        self.post_data['sportregistration_set-TOTAL_FORMS'] = 3

        response = self.client.post(self.url, data=self.post_data, follow=True)
        sr = SportRegistration.objects.filter(user=self.user)
        self.assertEqual(sr.count(), 3)
        self.assertRedirects(response, reverse('sport:finish_sport_registration'))

    def test_post_two_forms_same_sport(self):
        form_data = {
            'sportregistration_set-0-sport': self.ice_hockey.id,
            'sportregistration_set-0-roles': ['Referee', 'Manager'],
            'sportregistration_set-1-sport': self.ice_hockey.id,
            'sportregistration_set-1-roles': ['Player', 'Coach']
        }
        self.post_data.update(form_data)
        self.post_data['sportregistration_set-TOTAL_FORMS'] = 2
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 1, 'sport',
                                'Only one form can have {sport} selected. Choose another sport, or the "---------" value.'.format(
                                        sport=self.ice_hockey))

    def test_post_one_invalid_form(self):
        form_data = {
            'sportregistration_set-0-sport': '',
        }
        self.post_data.update(form_data)
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'sport', 'This field is required.')
        self.assertFormsetError(response, 'formset', 0, 'roles', 'This field is required.')

    def test_post_two_invalid_forms(self):
        form_data = {
            'sportregistration_set-0-sport': '',
            'sportregistration_set-1-sport': '',
            'sportregistration_set-1-roles': ['Player'],
        }
        self.post_data.update(form_data)
        self.post_data['sportregistration_set-TOTAL_FORMS'] = 2
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'sport', 'This field is required.')
        self.assertFormsetError(response, 'formset', 1, 'sport', 'This field is required.')
