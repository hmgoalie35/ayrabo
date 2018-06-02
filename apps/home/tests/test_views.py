from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from sports.tests import SportRegistrationFactory
from users.tests import UserFactory


class HomeViewTests(BaseTestCase):
    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'

    def test_unauthenticated(self):
        response = self.client.get(reverse('home'))
        self.assert_200(response)
        self.assertTemplateUsed(response, 'home/anonymous_home.html')

    def test_authenticated_no_user_profile(self):
        user = UserFactory(email=self.email, password=self.password)
        SportRegistrationFactory(user=user)
        self.client.login(email=self.email, password=self.password)

        response = self.client.get(reverse('home'))

        self.assert_200(response)
        self.assertTemplateUsed(response, 'home/authenticated_home.html')


class AboutUsViewTests(BaseTestCase):
    def test_get(self):
        response = self.client.get(reverse('about_us'))

        self.assert_200(response)
        self.assertTemplateUsed(response, 'home/about_us.html')


class ContactUsViewTests(BaseTestCase):
    def test_get(self):
        response = self.client.get(reverse('contact_us'))

        self.assert_200(response)
        self.assertTemplateUsed(response, 'home/contact_us.html')

        context = response.context

        self.assertDictEqual(context.get('support_contact'), {
            'name': 'Harris Pittinsky',
            'email': 'harris@pittinsky.com'
        })
