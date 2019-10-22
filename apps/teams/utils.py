from django.urls import reverse

from seasons.models import Season
from seasons.utils import get_current_season_or_from_pk


def get_team_detail_schedule_url(team, season):
    kwargs = {'team_pk': team.pk}
    if season.is_current:
        return reverse('teams:schedule', kwargs=kwargs)
    kwargs.update({'season_pk': season.pk})
    return reverse('teams:seasons:schedule', kwargs=kwargs)


def get_team_detail_players_url(team):
    return reverse('teams:players', kwargs={'team_pk': team.pk})


def get_team_detail_season_rosters_url(team, season):
    kwargs = {'team_pk': team.pk}
    if season.is_current:
        return reverse('teams:season_rosters:list', kwargs=kwargs)
    kwargs.update({'season_pk': season.pk})
    return reverse('teams:seasons:season_rosters-list', kwargs=kwargs)


def get_team_detail_view_context(team, season_pk=None):
    division = team.division
    league = division.league
    season = get_current_season_or_from_pk(league, season_pk)
    return {
        'team_display_name': f'{team.name} - {division.name}',
        'season': season,  # Note `get_game_list_view_context` is also setting the same context key.
        'schedule_link': get_team_detail_schedule_url(team, season),
        'players_link': get_team_detail_players_url(team),
        'season_rosters_link': get_team_detail_season_rosters_url(team, season),
        'seasons': Season.objects.get_for_league(league=league)
    }
