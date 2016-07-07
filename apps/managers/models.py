from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import models

from sports.models import Sport
from teams.models import Team


class Manager(models.Model):
    user = models.ForeignKey(User)
    team = models.ForeignKey(Team)

    class Meta:
        unique_together = (('user', 'team'),)

    def clean(self):
        if 'Manager' not in self.user.userprofile.roles:
            raise ValidationError(
                    '{user} does not have the manager role assigned, please update their userprofile to include it'.format(
                            user=self.user.get_full_name()))

    def __str__(self):
        return 'Manager {full_name}'.format(full_name=self.user.get_full_name())
