from datetime import date

from django.db import models


class SeasonManager(models.Manager):
    def get_current(self, league):
        """
        This function takes into account the `copy_expiring_seasons` management command running (the season for next
        year being auto-created) and the new year occurring.

        We do not use `__gte` for the end date because it will overlap with `__lte` of the start date and return the
        season for next year (assuming the `copy_expiring_seasons` has run). `__gte` is not used because we are
        assuming the season for next year has already been created, so the `__lte` check will return the correct season
        for us.

        :param league: The league to get the current season for
        :return: The currently active season for the given league if exists, else None
        """
        today = date.today()
        qs = self.filter(league=league, start_date__lte=today, end_date__gt=today)
        return qs.first()

    def get_past(self, league):
        """
        Computes past seasons for the given league.

        We do not use `__lte` because we only treat the season as in the past if its end date has passed.

        :param league: The league to get past seasons for
        :return: Past seasons for the league
        """
        today = date.today()
        # Order matters, we want to display recently finished seasons first.
        return self.filter(league=league, end_date__lt=today).order_by('-end_date')
