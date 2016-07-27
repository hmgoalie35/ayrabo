from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import models

from leagues.models import League


class Referee(models.Model):
    user = models.ForeignKey(User)
    league = models.ForeignKey(League)

    class Meta:
        unique_together = (('user', 'league'),)

    def clean(self):
        if hasattr(self, 'user') and not self.user.userprofile.has_role('Referee'):
            raise ValidationError(
                    '{user} does not have the referee role assigned, please update their userprofile to include it'.format(
                            user=self.user.get_full_name()))

    def __str__(self):
        return 'Referee {full_name}'.format(full_name=self.user.get_full_name())
