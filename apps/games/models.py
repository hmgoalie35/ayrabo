import pytz
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from periods.models import HockeyPeriod


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
    status = models.CharField(verbose_name='Status', max_length=255, choices=GAME_STATUSES, default=GAME_STATUSES[0][0])
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

    def datetime_localized(self, dt):
        return dt.astimezone(pytz.timezone(self.timezone))

    def datetime_formatted(self, dt, default_format='%m/%d/%Y %I:%M %p %Z'):
        return self.datetime_localized(dt).strftime(default_format)

    def init_periods(self, duration):
        """
        Creates the 1st, 2nd, 3rd and OT1 periods for this game.

        :param duration: Duration of this period, must be a timedelta instance.
        """
        period_choices = HockeyPeriod.PERIOD_CHOICES[:4]
        for period_choice in period_choices:
            HockeyPeriod.objects.get_or_create(game=self, name=period_choice[0], duration=duration)

    def clean_datetime(self, dt):
        """
        Because we are activating the timezone specified in the user's profile, Django automatically interprets/displays
        datetimes in that timezone. For games we actually don't want this to happen because the user selects the
        timezone in the form. As a result, we need to remove the tz django automatically interprets in, convert
        that naive datetime to the tz specified for the game, and finally convert to UTC. In short this function takes
        an aware datetime, converts it to another timezone and then converts to utc.

        :param dt: An aware datetime
        :return: The datetime converted to UTC
        """
        # Remove the tzinfo that Django automatically interprets in (the tz set in the user's profile). `make_naive`
        # defaults to removing the currently active tz.
        naive_dt = timezone.make_naive(dt)
        # Convert to the correct timezone specified for this game.
        aware_dt = timezone.make_aware(naive_dt, pytz.timezone(self.timezone))
        # Convert to UTC.
        utc_dt = aware_dt.astimezone(pytz.utc)
        return utc_dt

    def clean(self):
        super().clean()
        if getattr(self, 'start', None) and getattr(self, 'end', None) and getattr(self, 'timezone', None):
            self.start = self.clean_datetime(self.start)
            self.end = self.clean_datetime(self.end)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} {} vs. {}'.format(self.datetime_formatted(self.start), self.home_team.name, self.away_team.name)


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
                                             default=HOCKEY_GOAL_VALUES[0][0])
    created = models.DateTimeField(verbose_name='Created', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Updated', auto_now=True)

    def clean(self):
        super().clean()
        if hasattr(self, 'type'):
            if self.type in ['pp', 'sh']:
                msg = 'This field is required for {} goals.'.format(self.get_type_display().lower())
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
