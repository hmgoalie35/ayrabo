from django.db import models

from common import managers
from common.models import TimestampedModel
from teams.models import Team


class Coach(TimestampedModel):
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

    user = models.ForeignKey('users.User', related_name='coaches', on_delete=models.PROTECT)
    position = models.CharField(max_length=255, verbose_name='Position', choices=POSITIONS)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    objects = managers.ActiveManager()

    class Meta:
        verbose_name = 'Coach'
        verbose_name_plural = 'Coaches'
        unique_together = (('user', 'team'),)

    def __str__(self):
        return 'Coach {last_name}'.format(last_name=self.user.last_name)
