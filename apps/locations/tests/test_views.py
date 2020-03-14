import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from locations.models import Location
from locations.tests import LocationFactory
from managers.tests import ManagerFactory
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class LocationDetailViewTests(BaseTestCase):
    url = 'locations:detail'

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)
        sport = SportFactory(name='Ice Hockey')
        SportRegistrationFactory(user=self.user, sport=sport, role=SportRegistration.MANAGER)
        ManagerFactory(user=self.user, team=TeamFactory(name='Icecats', division__league__sport=sport))
        self.location = LocationFactory(id=1, name='Iceland', street_number=3345, street='Hillside Ave',
                                        city='New Hyde Park', state='NY', zip_code='11040')
        self.login(email=self.email, password=self.password)

    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.format_url(slug='iceland'))

    def test_get(self):
        response = self.client.get(self.format_url(slug='iceland'))
        self.assertTemplateUsed(response, 'locations/location_detail.html')
        self.assert_200(response)

    def test_get_404(self):
        response = self.client.get(self.format_url(slug='location-does-not-exist'))
        self.assert_404(response)

    def test_get_context_data(self):
        response = self.client.get(self.format_url(slug='iceland'))
        context = response.context

        self.assertEqual(context.get('location').id, 1)
        self.assertEqual(context.get('address'), '3345 Hillside Ave, New Hyde Park, NY 11040')
        self.assertIsNotNone(context.get('GOOGLE_MAPS_API_KEY'))
        self.assertTrue(context.get('RUNNING_AUTOMATED_TESTS'))


class LocationAdminBulkUploadViewTests(BaseTestCase):
    def setUp(self):
        self.url = reverse('admin:locations_location_bulk_upload')
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.test_file_path = os.path.join(settings.BASE_DIR, 'static', 'csv_examples')
        self.user = UserFactory(email=self.email, password=self.password, is_staff=True)

    def test_post_valid_csv(self):
        self.login(email=self.email, password=self.password)
        with open(os.path.join(self.test_file_path, 'bulk_upload_locations_example.csv')) as f:
            response = self.client.post(self.url, {'file': f}, follow=True)
            self.assertHasMessage(response, 'Successfully created 2 locations')
            self.assertEqual(Location.objects.count(), 2)

    def test_post_invalid_csv(self):
        self.login(email=self.email, password=self.password)
        content = b'name, street_number, street, city, state, zip_code, phone_number, website\n\na,b,c,d,e,f,g,h'
        f = SimpleUploadedFile('test.csv', content)
        response = self.client.post(self.url, {'file': f}, follow=True)
        self.assertEqual(Location.objects.count(), 0)
        self.assertFormsetError(response, 'formset', 0, 'website', ['Enter a valid URL.'])
        self.assertFormsetError(response, 'formset', 0, 'phone_number', ['Enter a valid phone number.'])
