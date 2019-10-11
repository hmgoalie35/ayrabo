from ayrabo.utils.testing import BaseTestCase
from organizations.tests import OrganizationFactory
from users.models import Permission
from users.tests import PermissionFactory


class PermissionManagerTests(BaseTestCase):
    def setUp(self):
        self.organization = OrganizationFactory(name='My Organization')

    def test_get_permissions_for_object(self):
        perm1 = PermissionFactory(content_object=self.organization, name=Permission.ADMIN)
        perm2 = PermissionFactory(content_object=self.organization, name=Permission.ADMIN)
        PermissionFactory(content_object=OrganizationFactory(), name=Permission.ADMIN)

        qs = Permission.objects.get_permissions_for_object(Permission.ADMIN, self.organization)
        self.assertListEqual(list(qs.order_by('id')), [perm1, perm2])

        # Make sure the manager filters by permission name
        organization = OrganizationFactory()
        PermissionFactory(content_object=organization, name='my_permission')
        qs = Permission.objects.get_permissions_for_object(Permission.ADMIN, organization)
        self.assertListEqual(list(qs.order_by('id')), [])
