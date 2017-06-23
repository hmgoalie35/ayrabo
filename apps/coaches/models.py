from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import models

from common import managers
from sports.models import SportRegistration
from teams.models import Team


class Coach(models.Model):
    """
    Represents a coach in the system. A user can have many Coach objects related to them provided each coach object
    is for a different team.
    TLDR; A user can be a coach for multiple teams and a new coach object is created for each team.
    """
    HEAD_COACH = 'Head Coach'
    ASSISTANT_COACH = 'Assistant Coach'

    POSITIONS = (
        ('head_coach', HEAD_COACH),
        ('assistant_coach', ASSISTANT_COACH)
    )

    user = models.ForeignKey(User, related_name='coaches')
    position = models.CharField(max_length=255, verbose_name='Position', choices=POSITIONS)
    team = models.ForeignKey(Team)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    objects = managers.ActiveManager()

    class Meta:
        verbose_name = 'Coach'
        verbose_name_plural = 'Coaches'
        unique_together = (('user', 'team'),)

    def clean(self):
        # The hasattr method is needed for when the admin panel is used. A user or team may be omitted by accident.
        if hasattr(self, 'user') and hasattr(self, 'team'):
            sport = self.team.division.league.sport
            qs = SportRegistration.objects.filter(user=self.user, sport=sport)
            if qs.exists() and not qs.first().has_role('Coach'):
                raise ValidationError(
                        '{user} - {sport} might not have a sportregistration object or the '
                        'sportregistration object does not have the coach role assigned'.format(
                                user=self.user.email, sport=sport.name))

    def __str__(self):
        return 'Coach {last_name}'.format(last_name=self.user.last_name)
