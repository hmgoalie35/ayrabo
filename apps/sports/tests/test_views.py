from django.urls import reverse

from accounts.tests import UserFactory
from divisions.tests import DivisionFactory
from escoresheet.utils.testing_utils import BaseTestCase
from leagues.tests import LeagueFactory
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


class CreateSportRegistrationViewTests(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super(CreateSportRegistrationViewTests, cls).setUpClass()
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.division = DivisionFactory(name='Midget Minor AA', league=cls.league)
        TeamFactory(name='Green Machine IceCats', division=cls.division)
        cls.baseball = SportFactory(name='Baseball')
        cls.basketball = SportFactory(name='Basketball')

    def setUp(self):
        self.url = reverse('sportregistrations:create')
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.post_data = {
            'sportregistrations-TOTAL_FORMS': 1,
            'sportregistrations-INITIAL_FORMS': 0,
            'sportregistrations-MIN_NUM_FORMS': 1,
            'sportregistrations-MAX_NUM_FORMS': 3
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
        SportRegistrationFactory(sport=self.ice_hockey, user=self.user, is_complete=True)
        SportRegistrationFactory(sport=self.baseball, user=self.user, is_complete=True)
        SportRegistrationFactory(sport=self.basketball, user=self.user, is_complete=True)
        response = self.client.get(self.url, follow=True)
        self.assertHasMessage(response, 'You have already registered for all available sports. '
                                        'Check back later to see if any new sports have been added.')
        self.assertRedirects(response, reverse('home'))

    def test_form_only_displays_sports_not_registered_for(self):
        SportRegistrationFactory(sport=self.ice_hockey, user=self.user, is_complete=True)
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
        SportRegistrationFactory(sport=self.ice_hockey, user=self.user, is_complete=True)
        SportRegistrationFactory(sport=self.baseball, user=self.user, is_complete=True)
        SportRegistrationFactory(sport=self.basketball, user=self.user, is_complete=True)
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertHasMessage(response, 'You have already registered for all available sports. '
                                        'Check back later to see if any new sports have been added.')
        self.assertRedirects(response, reverse('home'))

    def test_valid_post_one_form(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': ['Player', 'Coach']
        }
        self.post_data.update(form_data)
        response = self.client.post(self.url, data=self.post_data, follow=True)
        sr = SportRegistration.objects.filter(user=self.user, sport=self.ice_hockey)
        self.assertTrue(sr.exists())
        self.assertEqual(sr.first().roles, ['Player', 'Coach'])
        url = 'sportregistrations:{role}:create'.format(role='players')
        self.assertRedirects(response, reverse(url, kwargs={'pk': sr.first().id}))

    def test_valid_post_two_forms(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': ['Player', 'Coach'],
            'sportregistrations-1-sport': self.basketball.id,
            'sportregistrations-1-roles': ['Player', 'Referee']
        }
        self.post_data.update(form_data)
        self.post_data['sportregistrations-TOTAL_FORMS'] = 2

        response = self.client.post(self.url, data=self.post_data, follow=True)
        sr = SportRegistration.objects.filter(user=self.user)
        self.assertEqual(sr.count(), 2)
        self.assertEqual(sr[0].roles, ['Player', 'Coach'])
        self.assertEqual(sr[1].roles, ['Player', 'Referee'])
        url = 'sportregistrations:{role}:create'.format(role='players')
        self.assertRedirects(response, reverse(url, kwargs={'pk': sr.first().id}))

    def test_valid_post_three_forms(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': ['Player', 'Coach'],
            'sportregistrations-1-sport': self.basketball.id,
            'sportregistrations-1-roles': ['Player', 'Referee'],
            'sportregistrations-2-sport': self.baseball.id,
            'sportregistrations-2-roles': ['Manager', 'Referee']
        }
        self.post_data.update(form_data)
        self.post_data['sportregistrations-TOTAL_FORMS'] = 3

        response = self.client.post(self.url, data=self.post_data, follow=True)
        sr = SportRegistration.objects.filter(user=self.user)
        self.assertEqual(sr.count(), 3)
        url = 'sportregistrations:{role}:create'.format(role='players')
        self.assertRedirects(response, reverse(url, kwargs={'pk': sr.first().id}))

    def test_post_two_forms_same_sport(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': ['Referee', 'Manager'],
            'sportregistrations-1-sport': self.ice_hockey.id,
            'sportregistrations-1-roles': ['Player', 'Coach']
        }
        self.post_data.update(form_data)
        self.post_data['sportregistrations-TOTAL_FORMS'] = 2
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 1, 'sport',
                                'Only one form can have {sport} selected. '
                                'Choose another sport, or remove this form.'.format(sport=self.ice_hockey))

    def test_post_one_invalid_form(self):
        form_data = {
            'sportregistrations-0-sport': '',
        }
        self.post_data.update(form_data)
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'sport', 'This field is required.')
        self.assertFormsetError(response, 'formset', 0, 'roles', 'This field is required.')

    def test_post_two_invalid_forms(self):
        form_data = {
            'sportregistrations-0-sport': '',
            'sportregistrations-1-sport': '',
            'sportregistrations-1-roles': ['Player'],
        }
        self.post_data.update(form_data)
        self.post_data['sportregistrations-TOTAL_FORMS'] = 2
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'sport', 'This field is required.')
        self.assertFormsetError(response, 'formset', 1, 'sport', 'This field is required.')

    def test_post_empty_added_form(self):
        form_data = {
            'sportregistrations-0-sport': self.ice_hockey.id,
            'sportregistrations-0-roles': ['Player', 'Coach'],
            'sportregistrations-1-sport': [''],
        }

        # Could do an ORM call to grab the created obj, but its id is going to be 1.
        sr_id = 1

        self.post_data.update(form_data)
        self.post_data['sportregistrations-TOTAL_FORMS'] = 2
        response = self.client.post(self.url, data=self.post_data, follow=True)
        url = 'sportregistrations:{role}:create'.format(role='players')
        self.assertRedirects(response, reverse(url, kwargs={'pk': sr_id}))


class SportRegistrationDetailViewTests(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super(SportRegistrationDetailViewTests, cls).setUpClass()
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.division = DivisionFactory(name='Midget Minor AA', league=cls.league)
        cls.team = TeamFactory(name='Green Machine Icecats', division=cls.division)

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)
        self.sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True, roles_mask=15)
        self.url = reverse('sportregistrations:detail', kwargs={'pk': self.sr.pk})

        self.coach_data = {'user': self.user, 'team': self.team, 'position': 'Head Coach'}
        self.player_data = {'user': self.user, 'team': self.team, 'jersey_number': 23, 'handedness': 'Right',
                            'position': 'G', 'sport': self.ice_hockey}
        self.referee_data = {'user': self.user, 'league': self.league}
        self.manager_data = {'user': self.user, 'team': self.team}

        self.player, self.coach, self.referee, self.manager = self.create_related_objects(
                player_args=self.player_data,
                coach_args=self.coach_data,
                referee_args=self.referee_data,
                manager_args=self.manager_data)

        self.client.login(email=self.email, password=self.password)

    # GET
    def test_anonymous_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_not_object_owner(self):
        self.client.logout()
        other_user = UserFactory(email='otheruser@example.com', password=self.password)
        SportRegistrationFactory(user=other_user, sport=self.ice_hockey, is_complete=True)
        self.client.login(email=other_user.email, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'sports/sport_registration_detail.html')
        self.assertEqual(response.status_code, 200)

    def test_invalid_obj_id(self):
        response = self.client.get(reverse('sportregistrations:detail', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_context_populated(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertIsNotNone(context['sport_registration'])
        self.assertIsNotNone(context['sport_name'])
        self.assertIsNotNone(context['sr_roles'])
        self.assertIsNotNone(context['related_objects'])
