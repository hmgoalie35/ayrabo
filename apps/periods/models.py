from django.db import models

from common.models import TimestampedModel
from .model_fields import PeriodDurationField


class AbstractPlayingPeriod(TimestampedModel):
    """
    Abstract base class for periods, quarters, halves, etc.
    """
    duration = PeriodDurationField()
    complete = models.BooleanField(verbose_name='Complete', default=False)

    class Meta:
        abstract = True


class HockeyPeriod(AbstractPlayingPeriod):
    """
    Represents a period for hockey.
    """
    # 10 overtimes is ridiculous, but ya never know...
    ONE = '1'
    TWO = '2'
    THREE = '3'
    OT1 = 'ot1'
    OT2 = 'ot2'
    OT3 = 'ot3'
    OT4 = 'ot4'
    OT5 = 'ot5'
    OT6 = 'ot6'
    OT7 = 'ot7'
    OT8 = 'ot8'
    OT9 = 'ot9'
    OT10 = 'ot10'
    SHOOTOUT = 'so'
    PERIOD_CHOICES = (
        (ONE, '1st'),
        (TWO, '2nd'),
        (THREE, '3rd'),
        (OT1, 'Overtime 1'),
        (OT2, 'Overtime 2'),
        (OT3, 'Overtime 3'),
        (OT4, 'Overtime 4'),
        (OT5, 'Overtime 5'),
        (OT6, 'Overtime 6'),
        (OT7, 'Overtime 7'),
        (OT8, 'Overtime 8'),
        (OT9, 'Overtime 9'),
        (OT10, 'Overtime 10'),
        (SHOOTOUT, 'Shootout'),
    )

    game = models.ForeignKey('games.HockeyGame', verbose_name='Game', on_delete=models.PROTECT, related_name='periods')
    name = models.CharField(verbose_name='Name', choices=PERIOD_CHOICES, max_length=64)

    class Meta:
        unique_together = (('name', 'game'),)

    def __str__(self):
        return self.get_name_display()
