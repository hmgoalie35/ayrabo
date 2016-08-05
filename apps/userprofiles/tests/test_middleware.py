from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.tests.factories.UserFactory import UserFactory


class UserProfileCompletedMiddlewareTests(TestCase):
    def setUp(self):
        self.password = 'myweakpassword'
        self.user_with_profile = UserFactory.create(password=self.password)
        self.user_without_profile = UserFactory.create(password=self.password, userprofile=None)

    def test_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home/anonymous_home.html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'userprofiles/create.html')

    # Testing whitelisted urls
    def test_no_redirect_loop_create_profile_url(self):
        self.client.login(email=self.user_without_profile.email, password=self.password)
        response = self.client.get(reverse('profile:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userprofiles/create.html')

    def test_no_redirect_on_logout(self):
        self.client.login(email=self.user_without_profile.email, password=self.password)
        response = self.client.get(reverse('account_logout'))
        self.assertTemplateUsed(response, 'account/logout.html')
        self.assertTemplateNotUsed(response, 'userprofiles/create.html')
        self.assertEqual(response.status_code, 200)

    def test_no_userprofile(self):
        """
        A user without a userprofile should be prompted to create one.
        """
        self.client.login(email=self.user_without_profile.email, password=self.password)
        response = self.client.get(reverse('home'), follow=True)
        self.assertRedirects(response, reverse('profile:create'))

    def test_account_completed(self):
        self.client.login(email=self.user_with_profile.email, password=self.password)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/authenticated_home.html')
