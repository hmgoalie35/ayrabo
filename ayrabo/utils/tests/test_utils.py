from datetime import timedelta

from ayrabo.utils import timedelta_to_hours_minutes_seconds
from ayrabo.utils.testing import BaseTestCase


class UtilsTests(BaseTestCase):
    def test_timedelta_to_hours_minutes_seconds(self):
        hours, mins, secs = timedelta_to_hours_minutes_seconds(timedelta(hours=3, minutes=5, seconds=6, microseconds=5))
        self.assertEqual(hours, 3.0)
        self.assertEqual(mins, 5.0)
        self.assertEqual(secs, 6.000004999999874)
