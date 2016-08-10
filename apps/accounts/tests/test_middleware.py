from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.tests import UserFactory
from sports.tests import SportFactory
from sports.tests import SportRegistrationFactory


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
