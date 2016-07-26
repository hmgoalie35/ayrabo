from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import models

from sports.models import Sport
from teams.models import Team


class Coach(models.Model):
    HEAD_COACH = 'Head Coach'
    ASSISTANT_COACH = 'Assistant Coach'

    POSITIONS = (
        (HEAD_COACH, HEAD_COACH),
        (ASSISTANT_COACH, ASSISTANT_COACH)
    )

    user = models.ForeignKey(User)
    position = models.CharField(max_length=255, verbose_name='Position', choices=POSITIONS)
    team = models.ForeignKey(Team)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')

    class Meta:
        verbose_name = 'Coach'
        verbose_name_plural = 'Coaches'
        unique_together = (('user', 'team'),)

    def clean(self):
        if 'Coach' not in self.user.userprofile.roles:
            raise ValidationError(
                    '{user} does not have the coach role assigned, please update their userprofile to include it'.format(
                            user=self.user.get_full_name()))

    def __str__(self):
        return 'Coach {full_name}'.format(full_name=self.user.get_full_name())
