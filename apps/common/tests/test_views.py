import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from users.tests import UserFactory


class CsvBulkUploadViewTests(BaseTestCase):
    """
    This base class is being tested via BulkUploadLocationsView. It tests to see if objects are actually created in the
    respective subclasses.
    """

    def setUp(self):
        self.url = reverse('bulk_upload_locations')
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.test_file_path = os.path.join(settings.BASE_DIR, 'static', 'csv_examples')
        self.user = UserFactory(email=self.email, password=self.password, is_staff=True)

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        result_url = '{}?next={}'.format(reverse('admin:login'), self.url)
        self.assertRedirects(response, result_url)

    def test_staff_member_required(self):
        email = 'user1@ayrabo.com'
        password = 'myweakpassword'
        UserFactory(email=email, password=password, is_staff=False)
        self.login(email=email, password=password)

        response = self.client.get(self.url)
        result_url = '{}?next={}'.format(reverse('admin:login'), self.url)
        self.assertRedirects(response, result_url)

    def test_get(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.url)
        self.assert_200(response)
        self.assertTemplateUsed(response, 'common/admin_bulk_upload.html')
        self.assertIsNotNone(response.context['form'])

    def test_post(self):
        self.login(email=self.email, password=self.password)
        f = SimpleUploadedFile('test.csv', b'hello world')
        response = self.client.post(self.url, {'file': f})
        self.assertRedirects(response, self.url)
