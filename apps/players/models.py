from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from leagues.models import League
from sports.models import Sport
from teams.models import Team


class Player(models.Model):
    """
    An abstract base class used to represent a Player. It contains fields common to all players.
    Sub classes shall add custom fields for their specific sport.
    Because every sport has different positions, terms for handedness, etc, player models must be created for every sport.
    """

    MIN_JERSEY_NUMBER = 0
    MAX_JERSEY_NUMBER = 99

    user = models.ForeignKey(User)
    sport = models.ForeignKey(Sport)
    # TODO add in team/player history model to keep track of a player's teams throughout their career
    team = models.ForeignKey(Team)
    jersey_number = models.SmallIntegerField(verbose_name='Jersey Number',
                                             validators=[MinValueValidator(MIN_JERSEY_NUMBER), MaxValueValidator(MAX_JERSEY_NUMBER)])
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')

    @property
    def league(self):
        return self.team.division.league.full_name

    @property
    def division(self):
        return self.team.division.name

    def clean(self):
        if hasattr(self, 'user') and not self.user.userprofile.has_role('Player'):
            raise ValidationError(
                    '{user} does not have the player role assigned, please update their userprofile to include it'.format(
                            user=self.user.get_full_name()))

    class Meta:
        abstract = True
        unique_together = (
            ('user', 'sport'),
            ('user', 'team'),
        )

    def __str__(self):
        return self.user.get_full_name()


class HockeyPlayer(Player):
    """
    A model representing a hockey player.
    """

    POSITIONS = (
        ('C', 'C'),
        ('LW', 'LW'),
        ('RW', 'RW'),
        ('LD', 'LD'),
        ('RD', 'RD'),
        ('G', 'G'),
    )

    HANDEDNESS = (
        ('Left', 'Left'),
        ('Right', 'Right'),
    )

    position = models.CharField(max_length=255, choices=POSITIONS, verbose_name='Position')
    handedness = models.CharField(max_length=255, choices=HANDEDNESS, verbose_name='Shoots')
    # might need to move jersey_number into this model

    def clean(self):
        super(HockeyPlayer, self).clean()
        if hasattr(self, 'team'):
            # If we do not exclude the current user this validation error will always be triggered.
            qs = HockeyPlayer.objects.filter(team=self.team, jersey_number=self.jersey_number).exclude(user=self.user)
            if qs.exists():
                error_msg = 'Please choose another number, {jersey_number} is currently unavailable for {team}'.format(
                        jersey_number=self.jersey_number, team=self.team.name)
                raise ValidationError({
                    'jersey_number': _(error_msg)})
