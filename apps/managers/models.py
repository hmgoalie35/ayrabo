from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import models
from django.utils import timezone

from common import managers
from sports.models import SportRegistration
from teams.models import Team


class Manager(models.Model):
    """
    Represents a manager in the system. A user can have many manager objects related to them provided each manager
    object is for a different team.
    TLDR; A user can be a manager for multiple teams and a new manager object is created for each team.
    """
    user = models.ForeignKey(User, related_name='managers')
    team = models.ForeignKey(Team)
    created = models.DateTimeField(default=timezone.now, verbose_name='Created')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    objects = managers.ActiveManager()

    class Meta:
        unique_together = (('user', 'team'),)

    def clean(self):
        # hasattr is needed for when admin panel is used where an object w/o a user or team could be created.
        if hasattr(self, 'user') and hasattr(self, 'team'):
            sport = self.team.division.league.sport
            qs = SportRegistration.objects.filter(user=self.user, sport=sport)
            if qs.exists() and not qs.first().has_role('Manager'):
                raise ValidationError(
                        '{user} - {sport} might not have a sportregistration object or the '
                        'sportregistration object does not have the manager role assigned'.format(
                                user=self.user.email, sport=sport.name))

    def __str__(self):
        return 'Manager {last_name}'.format(last_name=self.user.last_name)
