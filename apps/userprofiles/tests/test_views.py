import factory
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from coaches.tests import CoachFactory
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from players.tests import HockeyPlayerFactory
from referees.tests import RefereeFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from userprofiles.models import UserProfile
from userprofiles.tests import UserProfileFactory
from users.tests import UserFactory


class UserProfileCreateViewTests(BaseTestCase):
    url = 'account_complete_registration'

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.baseball = SportFactory(name='Baseball')
        self.post_data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        del self.post_data['user']
        self.user = UserFactory.create(email=self.email, password=self.password, userprofile=None)
        self.login(email=self.email, password=self.password)

    def test_sport_registrations_complete_user_has_userprofile(self):
        UserProfileFactory(user=self.user)
        SportRegistrationFactory(user=self.user)
        response = self.client.get(self.format_url(), follow=True)
        self.assertRedirects(response, reverse('home'))

    # General
    def test_login_required(self):
        self.client.logout()
        url = self.format_url()
        response = self.client.get(url)
        self.assertRedirects(response, self.get_login_required_url(url))

    def test_userprofile_already_created(self):
        self.client.logout()
        user_with_profile = UserFactory.create(password=self.password)
        self.client.login(email=user_with_profile.email, password=self.password)
        response = self.client.get(self.format_url())
        self.assertRedirects(response, reverse('sportregistrations:create'))

    # GET
    def test_get(self):
        response = self.client.get(self.format_url())
        self.assertTemplateUsed(response, 'userprofiles/userprofile_create.html')
        self.assert_200(response)

    # POST
    def test_post_valid_data(self):
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('sportregistrations:create'))
        # Make sure `user` is set to request.user on the userprofile instance
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_post_invalid_data(self):
        self.post_data.pop('gender')
        self.post_data.pop('height')
        self.post_data.pop('weight')
        self.post_data.pop('birthday')

        response = self.client.post(self.format_url(), data=self.post_data)

        self.assertFormError(response, 'form', 'gender', 'This field is required.')
        self.assertFormError(response, 'form', 'height', 'This field is required.')
        self.assertFormError(response, 'form', 'weight', 'This field is required.')
        self.assertFormError(response, 'form', 'birthday', 'This field is required.')

    def test_post_invalid_height_formats(self):
        invalid_heights = ['5 7', '5 7\"', '5\' 7']
        for invalid_height in invalid_heights:
            self.post_data['height'] = invalid_height
            response = self.client.post(self.format_url(), data=self.post_data)
            self.assertFormError(response, 'form', 'height',
                                 'Invalid format, please enter your height according to the format below.')

    def test_post_invalid_weights(self):
        invalid_weights = [-1, -100, 0]
        for invalid_weight in invalid_weights:
            self.post_data['weight'] = invalid_weight
            response = self.client.post(self.format_url(), data=self.post_data)
            self.assertFormError(response, 'form', 'weight', 'Ensure this value is greater than or equal to 1.')

    def test_post_invalid_decimal_weights(self):
        invalid_weights = [.5, -.5]
        for invalid_weight in invalid_weights:
            self.post_data['weight'] = invalid_weight
            response = self.client.post(self.format_url(), data=self.post_data)
            self.assertFormError(response, 'form', 'weight', 'Enter a whole number.')


class UserProfileUpdateViewTests(BaseTestCase):
    url = 'account_home'

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'

        self.post_data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)

        self.user = UserFactory.create(email=self.email, password=self.password)
        self.sport = SportFactory(name='Ice Hockey')
        SportRegistrationFactory(user=self.user, sport=self.sport, is_complete=True)
        self.login(email=self.email, password=self.password)

    # General
    def test_login_required(self):
        self.client.logout()
        url = self.format_url()
        response = self.client.get(self.format_url())
        self.assertRedirects(response, self.get_login_required_url(url))

    # GET
    def test_get(self):
        response = self.client.get(self.format_url())
        self.assertTemplateUsed(response, 'userprofiles/userprofile_update.html')
        self.assert_200(response)

    def test_context_populated(self):
        self.client.logout()
        user = UserFactory(email='testing@ayrabo.com', password=self.password)
        self.client.login(email='testing@ayrabo.com', password=self.password)
        league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=self.sport)
        division = DivisionFactory(name='Midget Minor AA', league=league)
        team = TeamFactory(name='Green Machine Icecats', division=division)
        sr = SportRegistrationFactory(user=user, sport=self.sport)
        sr.set_roles(['Player', 'Coach', 'Manager', 'Referee'])
        manager = [ManagerFactory(user=user, team=team)]
        player = [HockeyPlayerFactory(user=user, team=team, sport=self.sport)]
        coach = [CoachFactory(user=user, team=team)]
        referee = [RefereeFactory(user=user, league=league)]
        response = self.client.get(self.format_url())

        data = response.context['data'].get(sr)
        self.assertEqual(data.get('sport'), sr.sport)
        self.assertEqual(data.get('roles'), ['Player', 'Coach', 'Referee', 'Manager'])
        related_objects = data.get('related_objects')
        self.assertEqual(list(related_objects.get('Player')), player)
        self.assertEqual(list(related_objects.get('Coach')), coach)
        self.assertEqual(list(related_objects.get('Referee')), referee)
        self.assertEqual(list(related_objects.get('Manager')), manager)
        self.assertEqual(response.context['active_tab'], 'my_account')

    # POST
    # No need to test invalid values for height, weight, etc. That is done above (the forms are almost identical)
    def test_post_no_changed_data(self):
        self.post_data.pop('gender')
        self.post_data.pop('birthday')
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('account_home'))

    def test_post_changed_data(self):
        # calling the factory will generate random values for all fields
        self.post_data.pop('gender')
        self.post_data.pop('birthday')
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        success_msg = 'Your account has been updated.'
        self.assertHasMessage(response, success_msg)
        self.assertTemplateUsed('userprofiles/userprofile_update.html')

    def test_userprofile_exists_in_context(self):
        self.post_data.pop('gender')
        self.post_data.pop('birthday')
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        self.assertIn('userprofile', response.context)
