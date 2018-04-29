from django.db import models

from common.models import TimestampedModel


class AbstractPlayingPeriod(TimestampedModel):
    """
    Abstract base class for periods, quarters, halves, etc.
    """
    duration = models.DurationField(verbose_name='Duration')
    complete = models.BooleanField(verbose_name='Complete', default=False)

    class Meta:
        abstract = True


class HockeyPeriod(AbstractPlayingPeriod):
    """
    Represents a period for hockey.
    """
    # 10 overtimes is ridiculous, but ya never know...
    PERIOD_CHOICES = (
        ('1', '1st'),
        ('2', '2nd'),
        ('3', '3rd'),
        ('ot1', 'Overtime 1'),
        ('ot2', 'Overtime 2'),
        ('ot3', 'Overtime 3'),
        ('ot4', 'Overtime 4'),
        ('ot5', 'Overtime 5'),
        ('ot6', 'Overtime 6'),
        ('ot7', 'Overtime 7'),
        ('ot8', 'Overtime 8'),
        ('ot9', 'Overtime 9'),
        ('ot10', 'Overtime 10'),
        ('so', 'Shootout'),
    )

    game = models.ForeignKey('games.HockeyGame', verbose_name='Game', on_delete=models.PROTECT, related_name='periods')
    name = models.CharField(verbose_name='Name', choices=PERIOD_CHOICES, max_length=64)

    class Meta:
        unique_together = (('name', 'game'),)

    def __str__(self):
        return self.get_name_display()
