import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from teams.models import Team
from users.tests import UserFactory


class BulkUploadTeamsViewTests(BaseTestCase):
    def setUp(self):
        self.url = reverse('bulk_upload_teams')
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.test_file_path = os.path.join(settings.BASE_DIR, 'static', 'csv_examples')
        self.user = UserFactory(email=self.email, password=self.password, is_staff=True)

    def test_post_valid_csv(self):
        self.client.login(email=self.email, password=self.password)
        with open(os.path.join(self.test_file_path, 'bulk_upload_teams_example.csv')) as f:
            response = self.client.post(self.url, {'file': f}, follow=True)
            self.assertHasMessage(response, 'Successfully created 2 team object(s)')
            self.assertEqual(Team.objects.count(), 2)

    def test_post_invalid_csv(self):
        self.client.login(email=self.email, password=self.password)
        content = b'name, street_number, street, city, state, zip_code, phone_number, website\n\na,b,c,d,e,f,g,h'
        f = SimpleUploadedFile('test.csv', content)
        response = self.client.post(self.url, {'file': f}, follow=True)
        self.assertEqual(Team.objects.count(), 0)
        self.assertFormsetError(response, 'formset', 0, 'website', ['Enter a valid URL.'])
        self.assertFormsetError(response, 'formset', 0, 'phone_number', ['Enter a valid phone number.'])
