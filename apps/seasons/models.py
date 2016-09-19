import logging

from django.core.validators import ValidationError
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from teams.models import Team

logger = logging.getLogger()


class Season(models.Model):
    division = models.ForeignKey('divisions.Division', unique_for_year='start_date')
    teams = models.ManyToManyField(Team)
    start_date = models.DateField(verbose_name='Start Date')
    end_date = models.DateField(verbose_name='End Date')

    class Meta:
        ordering = ['-end_date', '-start_date']
        unique_together = (
            ('start_date', 'division'),
            ('end_date', 'division'),
        )

    def clean(self):
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError({
                'end_date': "The season's end date must be after the season's start date."
            })

    def __str__(self):
        return '{start_year}-{end_year} Season'.format(start_year=self.start_date.year, end_year=self.end_date.year)


@receiver(m2m_changed, sender=Season.teams.through)
def validate_season_divisions(action, instance, pk_set, reverse, **kwargs):
    """
    This function validates that teams/seasons being added to the manytomany relationship between the two
    are in the same division, which also means they are in the same league, sport, etc.
    This function does not raise a validation error, it simply removes the pks from pk_set if the pks aren't in the
    same division as instance so those pks are never added to the relationship by the RelatedManager
    A validation error is not raised because it would have to be caught, which is possible in the views, but the admin
    would break.

    This function is meant to work in conjunction with a model form, i.e. SeasonAdminForm that will actually display
    form errors if a user ever needs to manually add teams to a season.

    :param action: The type of m2m action that has occurred.
    :param instance: The object being acted upon (being updated). Can be of class Team or Season depending on reverse.
    :param pk_set: List of pks for objects being added
    :param reverse: True if team_obj.season_set was used, False if season_obj.teams was used
    :param kwargs: Other kwargs sent by the signal
    """
    if action == 'pre_add':
        if reverse:
            # i.e. team_obj.season_set.add(season_obj), so pk_set contains pks for season objects
            cls = Season
            error_msg = 'The {0} specified ({1} - pk={2}) is not configured for {3} - {4}'
        else:
            # i.e. season_obj.teams.add(team_obj), so pk_set contains pks for team objects
            cls = Team
            error_msg = 'The {0} specified ({1} - pk={2}) does not belong to {3} - {4}'

        errors = []
        pks = pk_set.copy()
        for pk in pks:
            qs = cls.objects.filter(pk=pk)
            if qs.exists():
                obj = qs.first()
                if obj.division_id != instance.division_id:
                    # Remove the pk from the set so it is not added
                    pk_set.remove(pk)
                    errors.append(error_msg.format(cls.__name__.lower(), str(obj), obj.pk, instance.division,
                                                   instance.division.league.full_name))
            else:
                logger.error('{cls} with pk {pk} does not exist'.format(cls=cls.__name__, pk=pk))
        if errors:
            logger.error('. '.join(errors))
            # raise ValidationError(errors)


class AbstractSeasonRoster(models.Model):
    season = models.ForeignKey(Season)
    team = models.ForeignKey(Team)
    default = models.BooleanField(default=False, verbose_name='Default Season Roster')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')

    class Meta:
        abstract = True
        ordering = ['created']
        get_latest_by = 'created'

    def __str__(self):
        return '{team}-{division}: {season}'.format(team=self.team, division=self.team.division, season=self.season)


class HockeySeasonRoster(AbstractSeasonRoster):
    players = models.ManyToManyField('players.HockeyPlayer')
