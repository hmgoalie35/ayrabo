from django.core.exceptions import ValidationError
from django.db import models

from common import managers
from common.models import TimestampedModel
from sports.models import SportRegistration


class Scorekeeper(TimestampedModel):
    user = models.ForeignKey('users.User', verbose_name='User')
    sport = models.ForeignKey('sports.Sport', verbose_name='Sport')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    objects = managers.ActiveManager()

    def clean(self):
        # The hasattr method is needed for when the admin panel is used. A user or sport may be omitted by accident.
        if hasattr(self, 'user') and hasattr(self, 'sport'):
            sport = self.sport
            user = self.user
            qs = SportRegistration.objects.filter(user=user, sport=sport)
            if qs.exists() and not qs.first().has_role('Scorekeeper'):
                raise ValidationError(
                    '{} - {} might not have a sportregistration object or the '
                    'sportregistration object does not have the scorekeeper role assigned'.format(user.email,
                                                                                                  sport.name))

    class Meta:
        unique_together = (('user', 'sport'),)

    def __str__(self):
        return '{} - {}'.format(self.user.email, self.sport.name)
