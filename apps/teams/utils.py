from django.urls import reverse

from seasons.models import Season
from seasons.utils import get_current_season_or_from_pk


def get_team_detail_view_context(team, season_pk=None):
    division = team.division
    league = division.league
    season = get_current_season_or_from_pk(league, season_pk)
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
