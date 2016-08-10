import factory
from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.tests import UserFactory
from coaches.tests import CoachFactory
from divisions.tests import DivisionFactory
from escoresheet.testing_utils import get_messages
from leagues.tests.factories.LeagueFactory import LeagueFactory
from managers.tests.factories.ManagerFactory import ManagerFactory
from players.tests.factories.PlayerFactory import HockeyPlayerFactory
from referees.tests.factories.RefereeFactory import RefereeFactory
from sports.tests.factories.SportFactory import SportFactory
from sports.tests.factories.SportRegistrationFactory import SportRegistrationFactory
from teams.tests.factories.TeamFactory import TeamFactory
from userprofiles.models import UserProfile
from .factories.UserProfileFactory import UserProfileFactory


class CreateUserProfileViewTests(TestCase):
    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.baseball = SportFactory(name='Baseball')
        self.post_data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        del self.post_data['user']
        self.user = UserFactory.create(email=self.email, password=self.password, userprofile=None)
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse('profile:create'))
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('profile:create'))
        self.assertRedirects(response, result_url)

    def test_correct_template(self):
        response = self.client.get(reverse('profile:create'))
        self.assertTemplateUsed(response, 'userprofiles/create.html')

    def test_200_status_code(self):
        response = self.client.get(reverse('profile:create'))
        self.assertEqual(response.status_code, 200)

    def test_form_in_context(self):
        response = self.client.get(reverse('profile:create'))
        self.assertIsNotNone(response.context['form'])

    def test_get_userprofile_already_created(self):
        self.client.logout()
        user_with_profile = UserFactory.create(password=self.password)
        self.client.login(email=user_with_profile.email, password=self.password)
        response = self.client.get(reverse('profile:create'))
        self.assertRedirects(response, reverse('sport:create_sport_registration'))

    # POST
    def test_post_anonymous_user(self):
        self.client.logout()
        response = self.client.post(reverse('profile:create'), data=self.post_data)
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('profile:create'))
        self.assertRedirects(response, result_url)

    def test_post_userprofile_already_created(self):
        self.client.logout()
        user_with_profile = UserFactory(password=self.password)
        self.client.login(email=user_with_profile.email, password=self.password)
        response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('sport:create_sport_registration'))

    def test_valid_post_data(self):
        response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('sport:create_sport_registration'))

    def test_user_attribute_is_set(self):
        self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    # Invalid POST data

    def test_no_height_weight_gender(self):
        self.post_data.pop('gender')
        self.post_data.pop('height')
        self.post_data.pop('weight')
        response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertFormError(response, 'form', 'gender', 'This field is required.')
        self.assertFormError(response, 'form', 'height', 'This field is required.')
        self.assertFormError(response, 'form', 'weight', 'This field is required.')

    def test_invalid_height_format(self):
        invalid_heights = ['5 7', '5 7\"', '5\' 7']
        for invalid_height in invalid_heights:
            self.post_data['height'] = invalid_height
            response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
            self.assertFormError(response, 'form', 'height', 'Invalid format, please use the following format: 5\' 7"')

    def test_negative_and_zero_weights(self):
        invalid_weights = [-1, -100, 0]
        for invalid_weight in invalid_weights:
            self.post_data['weight'] = invalid_weight
            response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
            self.assertFormError(response, 'form', 'weight', 'Ensure this value is greater than or equal to 1.')

    def test_decimal_weights(self):
        invalid_weights = [.5, -.5]
        for invalid_weight in invalid_weights:
            self.post_data['weight'] = invalid_weight
            response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
            self.assertFormError(response, 'form', 'weight', 'Enter a whole number.')


class UpdateUserProfileViewTests(TestCase):
    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'

        self.post_data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)

        self.user = UserFactory.create(email=self.email, password=self.password)
        self.sport = SportFactory(name='Ice Hockey')
        SportRegistrationFactory(user=self.user, sport=self.sport, is_complete=True)
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse('profile:update'))
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('profile:update'))
        self.assertRedirects(response, result_url)

    def test_correct_template(self):
        response = self.client.get(reverse('profile:update'))
        self.assertTemplateUsed(response, 'userprofiles/update.html')

    def test_200_status_code(self):
        response = self.client.get(reverse('profile:update'))
        self.assertEqual(response.status_code, 200)

    def test_context_populated(self):
        self.client.logout()
        user = UserFactory(email='testing@example.com', password=self.password)
        self.client.login(email='testing@example.com', password=self.password)
        league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=self.sport)
        division = DivisionFactory(name='Midget Minor AA', league=league)
        team = TeamFactory(name='Green Machine Icecats', division=division)
        sr = SportRegistrationFactory(user=user, sport=self.sport)
        sr.set_roles(['Player', 'Coach', 'Manager', 'Referee'])
        manager = ManagerFactory(user=user, team=team)
        player = HockeyPlayerFactory(user=user, team=team, sport=self.sport)
        coach = CoachFactory(user=user, team=team)
        referee = RefereeFactory(user=user, league=league)
        response = self.client.get(reverse('profile:update'))
        result = {
            sr:
                {'sport': sr.sport,
                 'roles': ['Player', 'Coach', 'Referee', 'Manager'],
                 'related_objects':
                     {'Player': player,
                      'Coach': coach,
                      'Manager': manager,
                      'Referee': referee}}}
        self.assertDictEqual(response.context['data'], result)

    # POST
    # No need to test invalid values for height, weight, etc. That is done above (the forms are almost identical)
    def test_post_anonymous_user(self):
        self.client.logout()
        self.post_data.pop('gender')
        self.post_data.pop('birthday')
        response = self.client.post(reverse('profile:update'), data=self.post_data, follow=True)
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('profile:update'))
        self.assertRedirects(response, result_url)

    def test_post_no_changed_data(self):
        self.post_data.pop('gender')
        self.post_data.pop('birthday')
        response = self.client.post(reverse('profile:update'), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('profile:update'))

    def test_post_changed_data(self):
        # calling the factory will generate random values for all fields
        self.post_data.pop('gender')
        self.post_data.pop('birthday')
        response = self.client.post(reverse('profile:update'), data=self.post_data, follow=True)
        success_msg = 'Your profile has been updated'
        self.assertIn(success_msg, get_messages(response))
        self.assertTemplateUsed('userprofiles/update.html')

    def test_userprofile_exists_in_context(self):
        self.post_data.pop('gender')
        self.post_data.pop('birthday')
        response = self.client.post(reverse('profile:update'), data=self.post_data, follow=True)
        self.assertIn('userprofile', response.context)
