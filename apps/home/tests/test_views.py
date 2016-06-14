from django.test import TestCase
from django.core.urlresolvers import reverse
from accounts.tests.factories.UserFactory import UserFactory


class HomeViewTests(TestCase):
    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/anonymous_home.html')

    def test_authenticated_no_user_profile(self):
        UserFactory.create(email=self.email, password=self.password, userprofile=None)
        self.client.login(email=self.email, password=self.password)
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('create_userprofile'))

    def test_authenticated_valid_user_profile(self):
        UserFactory.create(email=self.email, password=self.password)
        self.client.login(email=self.email, password=self.password)
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home/authenticated_home.html')
        self.assertEqual(response.status_code, 200)


class AboutUsViewTests(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse('about_us'))

    def test_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_renders_correct_template(self):
        self.assertTemplateUsed(self.response, 'home/about_us.html')


class ContactUsViewTests(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse('contact_us'))

    def test_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_renders_correct_template(self):
        self.assertTemplateUsed(self.response, 'home/contact_us.html')


