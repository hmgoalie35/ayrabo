import pytz
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class AbstractGame(models.Model):
    """
    Abstract class representing a game.
    """
    GAME_STATUSES = (
        ('scheduled', 'Scheduled'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    home_team = models.ForeignKey('teams.Team', verbose_name='Home Team', on_delete=models.PROTECT,
                                  related_name='home_games')
    away_team = models.ForeignKey('teams.Team', verbose_name='Away Team', on_delete=models.PROTECT,
                                  related_name='away_games')
    type = models.ForeignKey('common.GenericChoice', verbose_name='Game Type', on_delete=models.PROTECT,
                             related_name='+')
    point_value = models.ForeignKey('common.GenericChoice', verbose_name='Point Value', on_delete=models.PROTECT,
                                    related_name='+')
    status = models.CharField(verbose_name='Status', max_length=255, choices=GAME_STATUSES)
    location = models.ForeignKey('locations.Location', verbose_name='Location', on_delete=models.PROTECT,
                                 related_name='games')
    start = models.DateTimeField(verbose_name='Game Start')
    end = models.DateTimeField(verbose_name='Game End')
    # In forms, the default value will be the user's timezone (set in their profile)
    timezone = models.CharField(max_length=128, choices=settings.COMMON_TIMEZONES, verbose_name='Timezone')
    season = models.ForeignKey('seasons.Season', verbose_name='Season', on_delete=models.PROTECT,
                               related_name='games')
    created = models.DateTimeField(verbose_name='Created', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Updated', auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} {} vs. {}'.format(self.datetime_formatted(self.start), self.home_team.name, self.away_team.name)

    def datetime_localized(self, dt):
        return dt.astimezone(pytz.timezone(self.timezone))

    def datetime_formatted(self, dt, default_format='%m/%d/%Y %I:%M %p %Z'):
        return self.datetime_localized(dt).strftime(default_format)


class HockeyGame(AbstractGame):
    home_players = models.ManyToManyField('players.HockeyPlayer', verbose_name='Home Roster', related_name='home_games')
    away_players = models.ManyToManyField('players.HockeyPlayer', verbose_name='Away Roster', related_name='away_games')


class HockeyGoal(models.Model):
    HOCKEY_GOAL_VALUES = (
        (1, '1'),
    )

    HOCKEY_GOAL_TYPES = (
        ('e', 'Even Strength'),
        ('pp', 'Power play'),
        ('sh', 'Shorthanded'),
    )

    game = models.ForeignKey(HockeyGame, verbose_name='Game', on_delete=models.PROTECT, related_name='goals')
    period = models.ForeignKey('periods.HockeyPeriod', verbose_name='Period', on_delete=models.PROTECT,
                               related_name='goals')
    time = models.DurationField(verbose_name='Time')
    player = models.ForeignKey('players.HockeyPlayer', verbose_name='Player', on_delete=models.PROTECT,
                               related_name='goals')
    type = models.CharField(max_length=255, verbose_name='Type', choices=HOCKEY_GOAL_TYPES)
    penalty = models.ForeignKey('penalties.HockeyPenalty', verbose_name='Penalty', on_delete=models.PROTECT, null=True,
                                blank=True)
    empty_net = models.BooleanField(verbose_name='Empty Net', default=False)
    value = models.PositiveSmallIntegerField(verbose_name='Value', choices=HOCKEY_GOAL_VALUES,
                                             default=HOCKEY_GOAL_VALUES[0])
    created = models.DateTimeField(verbose_name='Created', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Updated', auto_now=True)

    def clean(self):
        super().clean()
        if hasattr(self, 'type'):
            if self.type in ['pp', 'sh']:
                msg = 'This field is required for {} goals'.format(self.get_type_display().lower())
                raise ValidationError({'penalty': msg})

    def __str__(self):
        return '{}: {}'.format(self.player.user.last_name, self.time)


class HockeyAssist(models.Model):
    player = models.ForeignKey('players.HockeyPlayer', verbose_name='Player', related_name='assists',
                               on_delete=models.PROTECT)
    goal = models.ForeignKey(HockeyGoal, verbose_name='Goal', related_name='assists', on_delete=models.PROTECT)
    created = models.DateTimeField(verbose_name='Created', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Updated', auto_now=True)

    def clean(self):
        super().clean()
        if hasattr(self, 'player') and hasattr(self, 'goal'):
            if self.player_id == self.goal.player_id:
                user = self.player.user
                gender = 'his' if user.userprofile.gender == 'male' else 'her'
                raise ValidationError(
                    {'player': '{} cannot have an assist on {} own goal.'.format(user.get_full_name(), gender)})

    class Meta:
        unique_together = (('player', 'goal'),)

    def __str__(self):
        return '{} {}'.format(self.player.user.last_name, self.goal)
