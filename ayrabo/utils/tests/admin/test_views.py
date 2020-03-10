from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from users.tests import UserFactory


class AdminBulkUploadViewTests(BaseTestCase):

    def setUp(self):
        self.url = reverse('admin:locations_location_bulk_upload')
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password, is_staff=True, is_superuser=True)

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'{reverse("admin:login")}?next={self.url}')

    def test_staff_member_required(self):
        email = 'user1@ayrabo.com'
        password = 'myweakpassword'
        UserFactory(email=email, password=password, is_staff=False)
        self.login(email=email, password=password)

        response = self.client.get(self.url)
        self.assertRedirects(response, f'{reverse("admin:login")}?next={self.url}')

    def test_get(self):
        self.login(user=self.user)
        response = self.client.get(self.url)
        context = response.context
        self.assert_200(response)
        self.assertTemplateUsed(response, 'admin/bulk_upload.html')
        self.assertIsNotNone(context['form'])
        self.assertEqual(context.get('site_title'), 'ayrabo')
        self.assertEqual(context.get('site_header'), 'ayrabo')

    def test_post(self):
        self.login(user=self.user)
        f = SimpleUploadedFile('test.csv', b'hello world')
        response = self.client.post(self.url, {'file': f})
        self.assertRedirects(response, reverse('admin:locations_location_changelist'))
