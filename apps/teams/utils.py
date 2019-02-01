from django.shortcuts import get_object_or_404
from django.urls import reverse

from seasons.models import Season


def get_season(league, season_pk):
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


def get_team_detail_view_context(team, season_pk=None):
    division = team.division
    league = division.league
    season = get_season(league, season_pk)
    schedule_link = reverse('teams:schedule', kwargs={'team_pk': team.pk})
    season_rosters_link = reverse('teams:season_rosters:list', kwargs={'team_pk': team.pk})
    if season is not None and season.expired:
        kwargs = {'team_pk': team.pk, 'season_pk': season.pk}
        schedule_link = reverse('teams:seasons:schedule', kwargs=kwargs)
        season_rosters_link = reverse('teams:seasons:season_rosters-list', kwargs=kwargs)
    return {
        'team_display_name': f'{team.name} - {division.name}',
        'season': season,  # Note `get_game_list_view_context` is also setting the same context key.
        'schedule_link': schedule_link,
        'season_rosters_link': season_rosters_link,
        'past_seasons': Season.objects.get_past(league=league)
    }
