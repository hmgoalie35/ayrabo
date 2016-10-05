from unittest.mock import Mock

from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.tests import UserFactory
from sports.tests import SportFactory, SportRegistrationFactory
from ..middleware import AccountAndSportRegistrationCompleteMiddleware


class AccountAndSportRegistrationCompleteMiddlewareTests(TestCase):
    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.baseball = SportFactory(name='Baseball')
        self.password = 'myweakpassword'
        self.user_with_profile = UserFactory(password=self.password)
        self.user_without_profile = UserFactory(password=self.password, userprofile=None)

    def test_anonymous_user(self):
        """
        Requests by anonymous users should be allowed through. (i.e. contact, about, anonymous home page, etc.)
        """
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home/anonymous_home.html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'userprofiles/create.html')
        self.assertTemplateNotUsed(response, 'sports/sport_registration_create.html')

    # Testing whitelisted urls
    def test_no_redirect_loop_create_profile_url(self):
        """
        Make sure accessing a whitelisted url does not lead to a redirect loop
        """
        self.client.login(email=self.user_without_profile.email, password=self.password)
        response = self.client.get(reverse('profile:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userprofiles/create.html')

    def test_no_redirect_loop_create_sport_registration_url(self):
        """
        Make sure accessing a whitelisted url does not lead to a redirect loop
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        response = self.client.get(reverse('sport:create_sport_registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sports/sport_registration_create.html')

    def test_no_redirect_loop_finish_sport_registration_url(self):
        """
        Make sure accessing a whitelisted url does not lead to a redirect loop
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        SportRegistrationFactory(user=self.user_with_profile, sport=self.ice_hockey, is_complete=False)
        SportRegistrationFactory(user=self.user_with_profile, sport=self.baseball, is_complete=False)
        response = self.client.get(reverse('sport:finish_sport_registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sports/sport_registration_finish.html')

    def test_no_redirect_on_logout(self):
        """
        Make sure accessing a whitelisted url does not lead to a redirect loop
        """
        self.client.login(email=self.user_without_profile.email, password=self.password)
        response = self.client.get(reverse('account_logout'))
        self.assertTemplateUsed(response, 'account/logout.html')
        self.assertTemplateNotUsed(response, 'userprofiles/create.html')
        self.assertTemplateNotUsed(response, 'sports/sport_registration_create.html')
        self.assertEqual(response.status_code, 200)

    def test_no_sport_registrations(self):
        """
        A user without any sport registrations should be prompted to create one.
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('sport:create_sport_registration'))

    def test_no_userprofile(self):
        """
        A user without a userprofile should be prompted to create one.
        """
        self.client.login(email=self.user_without_profile.email, password=self.password)
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('profile:create'))

    def test_incomplete_sport_registrations(self):
        """
        A user with incomplete sport registrations should be prompted to finish them up
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        SportRegistrationFactory(user=self.user_with_profile, sport=self.ice_hockey, is_complete=False)
        SportRegistrationFactory(user=self.user_with_profile, sport=self.baseball, is_complete=False)
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('sport:finish_sport_registration'))

    def test_account_completed(self):
        """
        A user with a valid profile, and at least one complete sport registration should be able to access any page url
        without the middleware kicking in
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        SportRegistrationFactory(user=self.user_with_profile, sport=self.ice_hockey, is_complete=True)
        SportRegistrationFactory(user=self.user_with_profile, sport=self.baseball, is_complete=True)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/authenticated_home.html')


class MiddlewareAddsRolesToSessionTests(TestCase):
    """
    This tests to make sure the middleware is adding the user roles to the session correctly
    """

    @classmethod
    def setUpClass(cls):
        super(MiddlewareAddsRolesToSessionTests, cls).setUpClass()
        cls.user = UserFactory(email='user@example.com', password='myweakpassword')
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')

    def setUp(self):
        self.middleware = AccountAndSportRegistrationCompleteMiddleware()
        self.hockey_sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True)
        self.baseball_sr = SportRegistrationFactory(user=self.user, sport=self.baseball, is_complete=True)
        self.request = Mock()
        self.request.user = self.user
        self.request.user.is_authenticated = Mock(return_value=True)
        self.request.path = '/'
        self.request.session = {}

    def test_single_sport_registration(self):
        self.hockey_sr.set_roles(['Player', 'Coach'])
        self.middleware.process_request(self.request)
        self.assertListEqual(['Player', 'Coach'], self.request.session.get('user_roles'))

    def test_multiple_sport_registrations(self):
        """
        This tests that all roles from all sport registrations are added to the session
        """
        self.hockey_sr.set_roles(['Referee'])
        self.baseball_sr.set_roles(['Manager'])
        self.middleware.process_request(self.request)
        self.assertListEqual(['Referee', 'Manager'], self.request.session.get('user_roles'))

    def test_same_role_not_duplicated(self):
        self.hockey_sr.set_roles(['Player', 'Coach', 'Referee'])
        self.baseball_sr.set_roles(['Coach', 'Manager'])
        self.middleware.process_request(self.request)

        self.assertEqual(self.request.session.get('user_roles').count('Coach'), 1)
