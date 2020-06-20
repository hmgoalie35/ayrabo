import datetime

import pytz
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone as timezone_util

from common.models import TimestampedModel
from periods.models import HockeyPeriod
from userprofiles.models import UserProfile


class AbstractGame(TimestampedModel):
    """
    Abstract class representing a game.
    """
    SCHEDULED = 'scheduled'
    POSTPONED = 'postponed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    IN_PROGRESS = 'in_progress'
    GAME_STATUSES = (
        (SCHEDULED, 'Scheduled'),
        (POSTPONED, 'Postponed'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed'),
        (IN_PROGRESS, 'In Progress'),
    )

    GRACE_PERIOD = datetime.timedelta(hours=24)

    home_team = models.ForeignKey('teams.Team', verbose_name='Home Team', on_delete=models.PROTECT,
                                  related_name='home_%(class)ss')
    away_team = models.ForeignKey('teams.Team', verbose_name='Away Team', on_delete=models.PROTECT,
                                  related_name='away_%(class)ss')
    type = models.ForeignKey('common.GenericChoice', verbose_name='Game Type', on_delete=models.PROTECT,
                             related_name='+')
    point_value = models.ForeignKey('common.GenericChoice', verbose_name='Point Value', on_delete=models.PROTECT,
                                    related_name='+')
    status = models.CharField(verbose_name='Status', max_length=255, choices=GAME_STATUSES, default=SCHEDULED)
    location = models.ForeignKey('locations.Location', verbose_name='Location', on_delete=models.PROTECT,
                                 related_name='%(class)ss')
    start = models.DateTimeField(verbose_name='Game Start')
    end = models.DateTimeField(verbose_name='Game End')
    # In forms, the default value will be the user's timezone (set in their profile)
    timezone = models.CharField(max_length=128, choices=settings.COMMON_TIMEZONES, verbose_name='Timezone')
    season = models.ForeignKey('seasons.Season', verbose_name='Season', on_delete=models.PROTECT,
                               related_name='%(class)ss')
    # Used to track which team this game was created for
    team = models.ForeignKey('teams.Team', null=True, verbose_name='Team', on_delete=models.PROTECT)
    created_by = models.ForeignKey('users.User', null=True, verbose_name='Created By',
                                   related_name='%(class)ss_created', on_delete=models.PROTECT)

    def datetime_localized(self, dt):
        return dt.astimezone(pytz.timezone(self.timezone))

    def datetime_formatted(self, dt, default_format='%m/%d/%Y %I:%M %p %Z'):
        return self.datetime_localized(dt).strftime(default_format)

    @property
    def start_formatted(self):
        return self.datetime_formatted(self.start)

    @property
    def end_formatted(self):
        return self.datetime_formatted(self.end)

    @property
    def is_in_progress(self):
        return self.status == self.IN_PROGRESS

    @property
    def is_scheduled(self):
        return self.status == self.SCHEDULED

    def can_update(self):
        return self.status not in [self.COMPLETED] and timezone_util.now() <= self.end + self.GRACE_PERIOD

    def can_initialize(self):
        # When the start date passes the second part of the clause will always be true, hence why we also check status
        return self.status in [self.SCHEDULED] and timezone_util.now() >= self.start - self.GRACE_PERIOD

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
        naive_dt = timezone_util.make_naive(dt)
        # Convert to the correct timezone specified for this game.
        aware_dt = timezone_util.make_aware(naive_dt, pytz.timezone(self.timezone))
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


class BaseballGame(AbstractGame):
    home_players = models.ManyToManyField('players.BaseballPlayer', verbose_name='Home Roster',
                                          related_name='home_games')
    away_players = models.ManyToManyField('players.BaseballPlayer', verbose_name='Away Roster',
                                          related_name='away_games')


class HockeyGoal(TimestampedModel):
    ONE = 1
    HOCKEY_GOAL_VALUES = (
        (ONE, '1'),
    )

    EVEN_STRENGTH = 'e'
    POWER_PLAY = 'pp'
    SHORTHANDED = 'sh'
    HOCKEY_GOAL_TYPES = (
        (EVEN_STRENGTH, 'Even Strength'),
        (POWER_PLAY, 'Power play'),
        (SHORTHANDED, 'Shorthanded'),
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
    value = models.PositiveSmallIntegerField(verbose_name='Value', choices=HOCKEY_GOAL_VALUES, default=ONE)

    def clean(self):
        super().clean()
        if hasattr(self, 'type'):
            if self.type in [self.POWER_PLAY, self.SHORTHANDED]:
                msg = 'This field is required for {} goals.'.format(self.get_type_display().lower())
                raise ValidationError({'penalty': msg})

    def __str__(self):
        return '{}: {}'.format(self.player.user.last_name, self.time)


class HockeyAssist(TimestampedModel):
    player = models.ForeignKey('players.HockeyPlayer', verbose_name='Player', related_name='assists',
                               on_delete=models.PROTECT)
    goal = models.ForeignKey(HockeyGoal, verbose_name='Goal', related_name='assists', on_delete=models.PROTECT)

    def clean(self):
        super().clean()
        if hasattr(self, 'player') and hasattr(self, 'goal'):
            if self.player_id == self.goal.player_id:
                user = self.player.user
                gender = 'his' if user.userprofile.gender == UserProfile.MALE else 'her'
                raise ValidationError(
                    {'player': '{} cannot have an assist on {} own goal.'.format(user.get_full_name(), gender)})

    class Meta:
        unique_together = (('player', 'goal'),)

    def __str__(self):
        return '{} {}'.format(self.player.user.last_name, self.goal)
