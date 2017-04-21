from coaches.models import Coach
from coaches.tests import CoachFactory
from escoresheet.utils.testing_utils import BaseTestCase


class ActiveManagerTests(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.c1 = CoachFactory()
        cls.c2 = CoachFactory(is_active=False)

    def test_excludes_inactive(self):
        self.assertNotIn(self.c2, Coach.objects.active())
