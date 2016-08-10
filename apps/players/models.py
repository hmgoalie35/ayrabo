from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from leagues.models import League
from sports.models import Sport, SportRegistration
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
                                             validators=[MinValueValidator(MIN_JERSEY_NUMBER),
                                                         MaxValueValidator(MAX_JERSEY_NUMBER)])
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')

    @property
    def league(self):
        return self.team.division.league.full_name

    @property
    def division(self):
        return self.team.division.name

    def clean(self):
        # hasattr is needed for when the admin panel is used, where an object w/o a user or team may be created by
        # accident
        if hasattr(self, 'user') and hasattr(self, 'sport'):
            qs = SportRegistration.objects.filter(user=self.user, sport=self.sport)
            if qs.exists() and not qs.first().has_role('Player'):
                raise ValidationError(
                        '{user} - {sport} might not have a sportregistration object or the sportregistration object does not have the player role assigned'.format(
                                user=self.user.email, sport=self.sport.name))

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


class BaseballPlayer(Player):
    """
    A model representing a baseball player
    """

    POSITIONS = (
        ('C', 'Catcher'),
        ('P', 'Pitcher'),
        ('1B', 'First Base'),
        ('2B', 'Second Base'),
        ('SS', 'Shortstop'),
        ('3B', 'Third Base'),
        ('LF', 'Left Field'),
        ('CF', 'Center Field'),
        ('RF', 'Right Field'),
    )

    CATCHES = (
        ('Left', 'Left'),
        ('Right', 'Right'),
    )

    BATS = (
        ('Left', 'Left'),
        ('Right', 'Right'),
    )

    # TODO definitely need to add more fields, im definitely missing stuff
    position = models.CharField(max_length=255, choices=POSITIONS, verbose_name='Position')
    catches = models.CharField(max_length=255, choices=CATCHES, verbose_name='Catches')
    bats = models.CharField(max_length=255, choices=BATS, verbose_name='Bats')

    def clean(self):
        super(BaseballPlayer, self).clean()
        if hasattr(self, 'team'):
            # If we do not exclude the current user this validation error will always be triggered.
            qs = BaseballPlayer.objects.filter(team=self.team, jersey_number=self.jersey_number).exclude(user=self.user)
            if qs.exists():
                error_msg = 'Please choose another number, {jersey_number} is currently unavailable for {team}'.format(
                        jersey_number=self.jersey_number, team=self.team.name)
                raise ValidationError({
                    'jersey_number': _(error_msg)})


class BasketballPlayer(Player):
    POSITIONS = (
        ('PG', 'Point Guard'),
        ('SG', 'Shooting Guard'),
        ('SF', 'Small Forward'),
        ('PF', 'Power Forward'),
        ('C', 'Center'),
    )

    SHOOTS = (
        ('Left', 'Left'),
        ('Right', 'Right'),
    )

    position = models.CharField(max_length=255, choices=POSITIONS, verbose_name='Position')
    shoots = models.CharField(max_length=255, choices=SHOOTS, verbose_name='Shoots')

    def clean(self):
        super(BasketballPlayer, self).clean()
        if hasattr(self, 'team'):
            # If we do not exclude the current user this validation error will always be triggered.
            qs = BasketballPlayer.objects.filter(team=self.team, jersey_number=self.jersey_number).exclude(
                    user=self.user)
            if qs.exists():
                error_msg = 'Please choose another number, {jersey_number} is currently unavailable for {team}'.format(
                        jersey_number=self.jersey_number, team=self.team.name)
                raise ValidationError({
                    'jersey_number': _(error_msg)})
