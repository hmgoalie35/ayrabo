from escoresheet.utils.testing import BaseTestCase
from managers.models import Manager
from managers.tests import ManagerFactory


class ActiveManagerTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.m1 = ManagerFactory()
        cls.m2 = ManagerFactory(is_active=False)

    def test_excludes_inactive(self):
        self.assertNotIn(self.m2, Manager.objects.active())
