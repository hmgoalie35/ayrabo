from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import models

from sports.models import Sport, SportRegistration
from teams.models import Team


class Manager(models.Model):
    user = models.ForeignKey(User)
    team = models.ForeignKey(Team)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')

    class Meta:
        unique_together = (('user', 'team'),)

    def clean(self):
        if hasattr(self, 'user') and hasattr(self, 'team'):
            sport = self.team.division.league.sport
            qs = SportRegistration.objects.filter(user=self.user, sport=sport)
            if qs.exists() and not qs.first().has_role('Manager'):
                raise ValidationError(
                        '{user} - {sport} might not have a sportregistration object or the sportregistration object does not have the manager role assigned'.format(
                                user=self.user.email, sport=sport.name))

    def __str__(self):
        return 'Manager {full_name}'.format(full_name=self.user.get_full_name())
