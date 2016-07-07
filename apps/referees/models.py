from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import models

from divisions.models import Division


class Referee(models.Model):
    user = models.ForeignKey(User)
    division = models.ForeignKey(Division)

    class Meta:
        unique_together = (('user', 'division'),)

    def clean(self):
        if 'Referee' not in self.user.userprofile.roles:
            raise ValidationError(
                    '{user} does not have the referee role assigned, please update their userprofile to include it'.format(
                            user=self.user.get_full_name()))

    def __str__(self):
        return 'Referee {full_name}'.format(full_name=self.user.get_full_name())
