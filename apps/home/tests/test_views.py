from django.urls import reverse

from accounts.tests import UserFactory
from ayrabo.utils.testing import BaseTestCase
from sports.tests import SportRegistrationFactory


class HomeViewTests(BaseTestCase):
    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/anonymous_home.html')

    def test_authenticated_no_user_profile(self):
        user = UserFactory(email=self.email, password=self.password)
        SportRegistrationFactory(user=user)
        self.client.login(email=self.email, password=self.password)
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home/authenticated_home.html')


class AboutUsViewTests(BaseTestCase):
    def setUp(self):
        self.response = self.client.get(reverse('about_us'))

    def test_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_renders_correct_template(self):
        self.assertTemplateUsed(self.response, 'home/about_us.html')


class ContactUsViewTests(BaseTestCase):
    def setUp(self):
        self.response = self.client.get(reverse('contact_us'))

    def test_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_renders_correct_template(self):
        self.assertTemplateUsed(self.response, 'home/contact_us.html')
