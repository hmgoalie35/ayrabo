from unittest import mock

from ayrabo.utils.testing import BaseTestCase
from locations.admin import LocationAdmin
from locations.models import Location


class AdminBulkUploadMixinTests(BaseTestCase):
    def setUp(self):
        self.mock_admin_site = mock.Mock()
        self.mock_bulk_upload_view_class = mock.Mock()
        self.admin = LocationAdmin(model=Location, admin_site=self.mock_admin_site)
        self.admin.bulk_upload_view_class = self.mock_bulk_upload_view_class

    def test_get_url_name(self):
        self.assertEqual(self.admin.get_url_name(), 'locations_location_bulk_upload')

    def test_bulk_upload_view(self):
        self.admin.get_urls()
        self.mock_bulk_upload_view_class.as_view.assert_called_with(
            success_url='/admin/locations/location/',
            model=Location,
            model_form_class=None,
            model_formset_class=None,
            fields=(
                'name',
                'street',
                'street_number',
                'city',
                'state',
                'zip_code',
                'phone_number',
                'website'
            ),
            admin_site=self.mock_admin_site,
            extra_context={
                'title': 'Bulk upload locations',
                'opts': Location._meta,
            }
        )

    def test_get_urls(self):
        urls = self.admin.get_urls()
        url_names = [url.name for url in urls]
        self.assertIn('locations_location_bulk_upload', url_names)

    def test_changelist_actions(self):
        self.assertTupleEqual(self.admin.changelist_actions, ('bulk_upload', 'download_sample_bulk_upload_csv'))
