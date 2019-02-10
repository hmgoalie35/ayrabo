from django.shortcuts import get_object_or_404

from seasons.models import Season


def get_current_season_or_from_pk(league, season_pk):
    """
    Gets the current season or the season specified by the season_pk param for the given league.

    :param league: The league to get the season for. Also used to narrow down the queryset when a season_pk has been
        specified
    :param season_pk: Optional, the pk of the season to get.
    :raises Http404: If the season_pk DNE or it's a season_pk for another league.
    :return: The current season (if no season_pk was specified) else the season for the given season_pk.
    """
    if season_pk is None:
        # It's possible for this to return `None` if there is no current season for the league. That case should be
        # extremely rare, but may happen when writing tests.
        return Season.objects.get_current(league=league)
    return get_object_or_404(Season.objects.filter(league=league), pk=season_pk)
