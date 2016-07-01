from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.tests.factories.UserFactory import UserFactory


class UserProfileExistsMiddlewareTests(TestCase):
    def setUp(self):
        self.user_with_profile = UserFactory.create(password='myweakpassword')
        self.user_without_profile = UserFactory.create(password='myweakpassword', userprofile=None)

    def test_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home/anonymous_home.html')
        self.assertTemplateNotUsed(response, 'userprofiles/create.html')

    def test_no_redirect_on_logout(self):
        self.client.login(email=self.user_without_profile.email, password='myweakpassword')
        response = self.client.get(reverse('account_logout'))
        self.assertTemplateUsed(response, 'account/logout.html')
        self.assertTemplateNotUsed(response, 'userprofiles/create.html')
        self.assertEqual(response.status_code, 200)

    def test_no_redirect_loop_on_create_userprofile_page(self):
        self.client.login(email=self.user_without_profile.email, password='myweakpassword')
        response = self.client.get(reverse('create_userprofile'))
        self.assertTemplateUsed(response, 'userprofiles/create.html')
        self.assertEqual(response.status_code, 200)

    def test_redirects_when_no_userprofile_exists(self):
        self.client.login(email=self.user_without_profile.email, password='myweakpassword')
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('create_userprofile'))

    def test_no_redirect_when_profile_exists(self):
        self.client.login(email=self.user_with_profile.email, password='myweakpassword')
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home/authenticated_home.html')
        self.assertTemplateNotUsed(response, 'userprofiles/create.html')
        self.assertEqual(response.status_code, 200)

    def test_redirect_when_profile_not_complete(self):
        self.user_with_profile.userprofile.is_complete = False
        self.user_with_profile.userprofile.save()
        self.client.login(email=self.user_with_profile.email, password='myweakpassword')
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('finish_userprofile'))

    def test_no_redirect_when_profile_complete(self):
        self.client.login(email=self.user_with_profile.email, password='myweakpassword')
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home/authenticated_home.html')
        self.assertTemplateNotUsed(response, 'userprofiles/finish_profile.html')
        self.assertEqual(response.status_code, 200)

