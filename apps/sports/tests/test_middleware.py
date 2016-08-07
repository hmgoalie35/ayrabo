from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.tests.factories.UserFactory import UserFactory
from sports.tests.factories.SportRegistrationFactory import SportRegistrationFactory


class AccountAndSportRegistrationCompleteMiddlewareTests(TestCase):
    def setUp(self):
        self.password = 'myweakpassword'
        self.user = UserFactory(password=self.password)
        self.client.login(email=self.user.email, password=self.password)

    def test_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home/anonymous_home.html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'sports/sport_registration_create.html')

    # Testing whitelisted urls
    def test_no_redirect_loop_create_sport_registration_url(self):
        response = self.client.get(reverse('sport:create_sport_registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sports/sport_registration_create.html')

    def test_no_redirect_loop_finish_sport_registration_url(self):
        SportRegistrationFactory(user=self.user, sport__name='Ice Hockey')
        SportRegistrationFactory(user=self.user, sport__name='Baseball')
        response = self.client.get(reverse('sport:finish_sport_registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sports/sport_registration_finish.html')

    def test_no_redirect_on_logout(self):
        response = self.client.get(reverse('account_logout'))
        self.assertTemplateUsed(response, 'account/logout.html')
        self.assertTemplateNotUsed(response, 'sports/sport_registration_create.html')
        self.assertEqual(response.status_code, 200)

    def test_no_sport_registrations(self):
        """
        A user without any sport registrations should be prompted to create one.
        """
        response = self.client.get(reverse('home'), follow=True)
        self.assertRedirects(response, reverse('sport:create_sport_registration'))
