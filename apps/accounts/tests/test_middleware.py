from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from users.tests import UserFactory


class UserProfileCompleteMiddlewareTests(BaseTestCase):

    def setUp(self):
        self.password = 'myweakpassword'
        self.user_with_profile = UserFactory(password=self.password)
        self.user_without_profile = UserFactory(password=self.password, userprofile=None)

    def test_anonymous_user(self):
        """
        Requests by anonymous users should be allowed through. (i.e. contact, about, anonymous home page, etc.)
        """
        response = self.client.get(reverse('home'))
        self.assert_200(response)
        self.assertTemplateUsed(response, 'home/anonymous_home.html')

    def test_logout_url_whitelisted(self):
        """
        Make sure accessing a whitelisted url does not lead to a redirect loop
        """
        self.login(user=self.user_without_profile)
        response = self.client.get(reverse('account_logout'))
        self.assert_200(response)
        self.assertTemplateUsed(response, 'account/logout.html')

    def test_userprofile_exists(self):
        """
        A user with a valid profile should be able to access any page url without the middleware kicking in
        """
        self.login(user=self.user_with_profile)
        response = self.client.get(reverse('home'))
        self.assert_200(response)
        self.assertTemplateUsed(response, 'home/authenticated_home.html')
        self.assertTrue(self.get_session_value('is_registration_complete'))

    def test_userprofile_dne(self):
        """
        A user without a userprofile should be prompted to create one.
        """
        self.login(user=self.user_without_profile)
        response = self.client.get(reverse('home'), follow=True)
        self.assertRedirects(response, reverse('account_complete_registration'))
        self.assertFalse(self.get_session_value('is_registration_complete'))
        self.assertHasMessage(response, 'You must complete your account registration before browsing ayrabo.com.')

    def test_no_redirect_loop_create_profile_url(self):
        """
        We shouldn't be redirecting to the url the request is coming from
        """
        self.login(user=self.user_without_profile)
        response = self.client.get(reverse('account_complete_registration'))
        self.assert_200(response)
        self.assertTemplateUsed(response, 'userprofiles/userprofile_create.html')
