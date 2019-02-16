from collections import OrderedDict

from django.core.validators import MaxValueValidator, MinValueValidator, ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from common import managers
from common.models import TimestampedModel
from sports.models import Sport
from teams.models import Team
from users.models import User


class AbstractPlayer(TimestampedModel):
    """
    An abstract base class used to represent a Player. It contains fields common to all players.
    Sub classes shall add custom fields for their specific sport because every sport has different positions, terms for
    handedness, etc, player models must be created for every sport.
    """

    MIN_JERSEY_NUMBER = 0
    MAX_JERSEY_NUMBER = 99

    user = models.ForeignKey(User)
    sport = models.ForeignKey(Sport)
    team = models.ForeignKey(Team)
    jersey_number = models.SmallIntegerField(verbose_name='Jersey Number',
                                             validators=[MinValueValidator(MIN_JERSEY_NUMBER),
                                                         MaxValueValidator(MAX_JERSEY_NUMBER)])
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    objects = managers.ActiveManager()

    @property
    def league(self):
        return self.team.division.league

    @property
    def division(self):
        return self.team.division

    @property
    def fields(self):
        """
        Utility property used to display this model's fields and values in an html friendly way. This is needed due to
        subclasses having different names for fields.

        All subclasses shall override this function, call super and update the result of the super call with any extra
        fields. The `@property` decorator must also be applied.

        :return: OrderedDict where the keys are user friendly display names and the values are the value of the field.
        """
        fields = OrderedDict()
        fields['Team'] = self.team
        fields['Division'] = self.division
        fields['Jersey Number'] = self.jersey_number
        return fields

    @property
    def table_fields(self):
        """
        Utility property used to dynamically determine what columns in an HTML table should be displayed and the correct
        value for that column.

        :return: OrderedDict where keys are the column name and values are the column values.
        """
        fields = OrderedDict()
        fields.update({
            'Jersey Number': self.jersey_number,
            'Name': self.user.get_full_name()
        })
        return fields

    class Meta:
        abstract = True
        unique_together = (
            ('user', 'team'),
        )

    def __str__(self):
        return self.user.get_full_name()


class HockeyPlayer(AbstractPlayer):
    """
    A model representing a hockey player.
    """

    POSITIONS = (
        ('C', 'Center'),
        ('LW', 'Left Wing'),
        ('RW', 'Right Wing'),
        ('LD', 'Left Defense'),
        ('RD', 'Right Defense'),
        ('G', 'Goaltender'),
    )

    HANDEDNESS = (
        ('Left', 'Left'),
        ('Right', 'Right'),
    )

    position = models.CharField(max_length=255, choices=POSITIONS, verbose_name='Position')
    handedness = models.CharField(max_length=255, choices=HANDEDNESS, verbose_name='Shoots')

    @property
    def fields(self):
        fields = super().fields
        fields['Position'] = self.get_position_display()
        fields['Handedness'] = self.get_handedness_display()
        return fields

    @property
    def table_fields(self):
        fields = super().table_fields
        fields.update({
            'Position': self.get_position_display(),
            'Handedness': self.get_handedness_display()
        })
        return fields

    def clean(self):
        super().clean()
        if hasattr(self, 'team'):
            # If we do not exclude the current user this validation error will always be triggered.
            qs = HockeyPlayer.objects.active().filter(team=self.team, jersey_number=self.jersey_number).exclude(
                user=self.user)
            if qs.exists():
                error_msg = 'Please choose another number, {jersey_number} is currently unavailable for {team}'.format(
                    jersey_number=self.jersey_number, team=self.team.name)
                raise ValidationError({
                    'jersey_number': _(error_msg)})


class BaseballPlayer(AbstractPlayer):
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

    position = models.CharField(max_length=255, choices=POSITIONS, verbose_name='Position')
    catches = models.CharField(max_length=255, choices=CATCHES, verbose_name='Catches')
    bats = models.CharField(max_length=255, choices=BATS, verbose_name='Bats')

    @property
    def fields(self):
        fields = super().fields
        fields['Position'] = self.get_position_display()
        fields['Catches'] = self.get_catches_display()
        fields['Bats'] = self.get_bats_display()
        return fields

    @property
    def table_fields(self):
        fields = super().table_fields
        fields.update({
            'Position': self.get_position_display(),
            'Catches': self.get_catches_display(),
            'Bats': self.get_bats_display()
        })
        return fields

    def clean(self):
        super().clean()
        if hasattr(self, 'team'):
            # If we do not exclude the current user this validation error will always be triggered.
            qs = BaseballPlayer.objects.active().filter(team=self.team, jersey_number=self.jersey_number).exclude(
                user=self.user)
            if qs.exists():
                error_msg = 'Please choose another number, {jersey_number} is currently unavailable for {team}'.format(
                    jersey_number=self.jersey_number, team=self.team.name)
                raise ValidationError({
                    'jersey_number': _(error_msg)})


class BasketballPlayer(AbstractPlayer):
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

    @property
    def fields(self):
        fields = super().fields
        fields['Position'] = self.get_position_display()
        fields['Shoots'] = self.get_shoots_display()
        return fields

    @property
    def table_fields(self):
        fields = super().table_fields
        fields.update({
            'Position': self.get_position_display(),
            'Shoots': self.get_shoots_display()
        })
        return fields

    def clean(self):
        super().clean()
        if hasattr(self, 'team'):
            # If we do not exclude the current user this validation error will always be triggered.
            qs = BasketballPlayer.objects.active().filter(team=self.team, jersey_number=self.jersey_number).exclude(
                user=self.user)
            if qs.exists():
                error_msg = 'Please choose another number, {jersey_number} is currently unavailable for {team}'.format(
                    jersey_number=self.jersey_number, team=self.team.name)
                raise ValidationError({
                    'jersey_number': _(error_msg)})
