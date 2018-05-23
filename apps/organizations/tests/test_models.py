from django.db import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from organizations.tests import OrganizationFactory


class OrganizationModelTests(BaseTestCase):
    def setUp(self):
        self.organization = OrganizationFactory(name='Green Machine IceCats')

    def test_unique_name(self):
        with self.assertRaises(IntegrityError):
            OrganizationFactory(name='Green Machine IceCats')

    def test_clean_slug(self):
        self.assertEqual(self.organization.slug, 'green-machine-icecats')

    def test_to_string(self):
        self.assertEqual(str(self.organization), 'Green Machine IceCats')
