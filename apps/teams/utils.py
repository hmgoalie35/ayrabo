from django.shortcuts import get_object_or_404
from django.urls import reverse

from seasons.models import Season


def get_season(league, season_pk):
    if season_pk is None:
        return Season.objects.get_current(league=league)
    return get_object_or_404(Season.objects.filter(league=league), pk=season_pk)


def get_team_detail_view_context(team, season_pk=None):
    division = team.division
    league = division.league
    season = get_season(league, season_pk)
    schedule_link = reverse('teams:schedule', kwargs={'team_pk': team.pk})
    season_rosters_link = reverse('teams:season_rosters:list', kwargs={'team_pk': team.pk})
    if season.expired:
        schedule_link = reverse('teams:seasons:schedule', kwargs={'team_pk': team.pk, 'season_pk': season.pk})
    return {
        'team_display_name': f'{team.name} - {division.name}',
        'season': season,  # Note `get_game_list_view_context` is also setting the same context key.
        'schedule_link': schedule_link,
        'season_rosters_link': season_rosters_link,
        'past_seasons': Season.objects.get_past(league=league)
    }
