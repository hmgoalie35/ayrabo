from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import models

from leagues.models import League
from userprofiles.models import RolesMask


class Referee(models.Model):
    user = models.ForeignKey(User)
    league = models.ForeignKey(League)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')

    class Meta:
        unique_together = (('user', 'league'),)

    def clean(self):
        if hasattr(self, 'user') and hasattr(self, 'league'):
            sport = self.league.sport
            qs = RolesMask.objects.filter(user=self.user, sport=sport)
            if qs.exists() and not qs.first().has_role('Referee'):
                raise ValidationError(
                        '{user} - {sport} might not have a rolesmask object or the rolesmask object does not have the referee role assigned'.format(
                                user=self.user.email, sport=sport.name))

    def __str__(self):
        return 'Referee {full_name}'.format(full_name=self.user.get_full_name())
