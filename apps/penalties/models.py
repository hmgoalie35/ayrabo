from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from common.managers import GenericChoiceManager


class GenericPenaltyChoice(models.Model):
    content_type = models.ForeignKey(ContentType, verbose_name='Content Type', on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField(verbose_name='Object Id')
    content_object = GenericForeignKey()

    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description', blank=True)

    objects = GenericChoiceManager()

    class Meta:
        unique_together = (('name', 'content_type', 'object_id'),)

    def __str__(self):
        return self.name


class AbstractPenalty(models.Model):
    class Meta:
        abstract = True


class HockeyPenalty(AbstractPenalty):
    game = models.ForeignKey('games.HockeyGame', verbose_name='Game', related_name='penalties',
                             on_delete=models.PROTECT)
    period = models.ForeignKey('periods.HockeyPeriod', verbose_name='Period', related_name='penalties',
                               on_delete=models.PROTECT)
    type = models.ForeignKey(GenericPenaltyChoice, verbose_name='Penalty', on_delete=models.PROTECT,
                             related_name='+')
    duration = models.DurationField(verbose_name='Duration')
    player = models.ForeignKey('players.HockeyPlayer', verbose_name='Player', related_name='penalties',
                               on_delete=models.PROTECT)
    time_in = models.DurationField(verbose_name='Time In')
    time_out = models.DurationField(verbose_name='Time Out')
    created = models.DateTimeField(verbose_name='Created', default=timezone.now)
    updated = models.DateTimeField(verbose_name='Updated', auto_now=True)

    class Meta:
        verbose_name_plural = 'Hockey Penalties'

    def __str__(self):
        return '{}: {} {}'.format(self.player.user.last_name, self.duration, self.type.name)
