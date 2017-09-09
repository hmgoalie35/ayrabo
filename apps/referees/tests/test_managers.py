from escoresheet.utils.testing import BaseTestCase
from referees.models import Referee
from referees.tests import RefereeFactory


class ActiveManagerTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.r1 = RefereeFactory()
        cls.r2 = RefereeFactory(is_active=False)

    def test_excludes_inactive(self):
        self.assertNotIn(self.r2, Referee.objects.active())
