from seasons.models import Season


def get_team_detail_view_context(team):
    division = team.division
    league = division.league
    return {
        'team_display_name': f'{team.name} - {division.name}',
        'past_seasons': Season.objects.get_past(league=league)
    }
