from django.db import models

from common import managers
from common.models import TimestampedModel
from teams.models import Team


class Manager(TimestampedModel):
    """
    Represents a manager in the system. A user can have many manager objects related to them provided each manager
    object is for a different team.
    TLDR; A user can be a manager for multiple teams and a new manager object is created for each team.
    """
    user = models.ForeignKey('users.User', related_name='managers', on_delete=models.PROTECT)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    objects = managers.ActiveManager()

    class Meta:
        unique_together = (('user', 'team'),)

    def __str__(self):
        return 'Manager {last_name}'.format(last_name=self.user.last_name)
