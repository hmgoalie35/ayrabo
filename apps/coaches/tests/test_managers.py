from coaches.models import Coach
from coaches.tests import CoachFactory
from ayrabo.utils.testing import BaseTestCase


class ActiveManagerTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.c1 = CoachFactory()
        cls.c2 = CoachFactory(is_active=False)

    def test_excludes_inactive(self):
        self.assertNotIn(self.c2, Coach.objects.active())
