from escoresheet.utils.testing_utils import BaseTestCase
from managers.models import Manager
from managers.tests import ManagerFactory


class IsActiveManagerTests(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.m1 = ManagerFactory()
        cls.m2 = ManagerFactory(is_active=False)

    def test_excludes_inactive(self):
        self.assertNotIn(self.m2, Manager.objects.all())
