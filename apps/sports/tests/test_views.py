from django.test import TestCase
from account_custom.tests.factories.UserFactory import UserFactory
from .factories.SportFactory import SportFactory
from django.core.urlresolvers import reverse
import factory
from escoresheet.testing_utils import get_messages
from sports.models import Sport


class CreateSportViewTests(TestCase):
    def setUp(self):
        self.staff_user = UserFactory.create(is_staff=True)
        self.client.login(email=self.staff_user.email, password='myweakpassword')

    def test_get_request_non_staff_user(self):
        self.client.logout()
        self.normal_user = UserFactory.create()
        self.client.login(email=self.normal_user.email, password='myweakpassword')
        response = self.client.get(reverse('create_sport'), follow=True)
        self.assertIn('You do not have permission to access the requested page', get_messages(response))
        self.assertRedirects(response, reverse('home'))

    def test_post_request_non_staff_user(self):
        self.client.logout()
        self.normal_user = UserFactory.create()
        self.client.login(email=self.normal_user.email, password='myweakpassword')
        data = factory.build(dict, FACTORY_CLASS=SportFactory)
        response = self.client.post(reverse('create_sport'), data, follow=True)
        self.assertIn('You do not have permission to access the requested page', get_messages(response))
        self.assertRedirects(response, reverse('home'))


    # GET
    def test_correct_template(self):
        response = self.client.get(reverse('create_sport'))
        self.assertTemplateUsed(response, 'sports/create.html')

    def test_200_status_code(self):
        response = self.client.get(reverse('create_sport'))
        self.assertEqual(response.status_code, 200)

    # POST
    def test_valid_post_data(self):
        data = factory.build(dict, FACTORY_CLASS=SportFactory)
        response = self.client.post(reverse('create_sport'), data=data, follow=True)
        success_msg = '{sport} successfully created'.format(sport=data['name'].title())
        self.assertIn(success_msg, get_messages(response))
        self.assertRedirects(response, reverse('home'))

    def test_name_converted_to_titlecase(self):
        data = factory.build(dict, FACTORY_CLASS=SportFactory)
        self.client.post(reverse('create_sport'), data=data, follow=True)
        self.assertEqual(Sport.objects.first().name, data['name'].title())

    # Invalid POST data
    def test_no_name(self):
        data = factory.build(dict, FACTORY_CLASS=SportFactory)
        data.pop('name')
        response = self.client.post(reverse('create_sport'), data=data, follow=True)
        self.assertFormError(response, 'form', 'name', 'This field is required.')

    def test_duplicate_name(self):
        SportFactory.create(name='Ice Hockey')
        data = factory.build(dict, FACTORY_CLASS=SportFactory, name='Ice Hockey')
        response = self.client.post(reverse('create_sport'), data=data, follow=True)
        self.assertFormError(response, 'form', 'name', 'Sport with this name already exists (case-insensitive)')

    def test_duplicate_slug(self):
        SportFactory.create(name='Ice Hockey')
        data = factory.build(dict, FACTORY_CLASS=SportFactory, name='ice hockey')
        response = self.client.post(reverse('create_sport'), data=data, follow=True)
        self.assertFormError(response, 'form', 'name', 'Sport with this name already exists (case-insensitive)')
