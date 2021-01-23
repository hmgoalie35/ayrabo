from django.core.exceptions import ValidationError

from ayrabo.utils.testing import BaseTestCase
from ayrabo.utils.testing.models import TestingModel
from periods.model_fields import PeriodDurationField


class PlayingPeriod(TestingModel):
    duration = PeriodDurationField()


class PeriodDurationFieldTests(BaseTestCase):
    def test_validators(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is greater than or equal to 1.'):
            PlayingPeriod.objects.create(duration=0).full_clean()

        with self.assertRaisesMessage(ValidationError, 'Ensure this value is less than or equal to 60.'):
            PlayingPeriod.objects.create(duration=100).full_clean()

        instance = PlayingPeriod.objects.create(duration=25)
        instance.full_clean()
        self.assertEqual(instance.duration, 25)
