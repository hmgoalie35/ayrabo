from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .form_fields import PeriodDurationField as PeriodDurationFormField


PERIOD_DURATION_MIN = 1
PERIOD_DURATION_MAX = 60


class PeriodDurationField(models.IntegerField):
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'null': True,
            'validators': [MinValueValidator(PERIOD_DURATION_MIN), MaxValueValidator(PERIOD_DURATION_MAX)],
            'help_text': 'In minutes',
        })
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.update({
            'form_class': PeriodDurationFormField,
        })
        return super().formfield(**kwargs)
