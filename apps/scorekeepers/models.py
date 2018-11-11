from django.db import models

from common import managers
from common.models import TimestampedModel


class Scorekeeper(TimestampedModel):
    user = models.ForeignKey('users.User', verbose_name='User')
    sport = models.ForeignKey('sports.Sport', verbose_name='Sport')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    objects = managers.ActiveManager()

    class Meta:
        unique_together = (('user', 'sport'),)

    def __str__(self):
        return '{} - {}'.format(self.user.email, self.sport.name)
