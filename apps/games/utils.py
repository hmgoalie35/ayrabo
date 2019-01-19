from django.db.models import Q

from games.mappings import get_game_model_cls
from managers.models import Manager
from scorekeepers.models import Scorekeeper


def get_game_list_context(user, sport):
    """
    Computes common values used when listing games. Mainly the team ids the user is a manager for and if the user is a
    scorekeeper.

    :param user: User to get managers for
    :param sport: Only include managers for this sport
    :return: Dict containing common values for listing games
    """
    manager_objects_for_user = Manager.objects.active().filter(user=user)
    # It's more efficient to compute this once and use `in` rather than query to see if a manager exists for the user
    # and some team.
    team_ids_managed_by_user = manager_objects_for_user.filter(team__division__league__sport=sport).values_list(
        'team_id', flat=True)
    is_scorekeeper = Scorekeeper.objects.active().filter(user=user, sport=sport).exists()
    return {
        'team_ids_managed_by_user': team_ids_managed_by_user,
        'is_scorekeeper': is_scorekeeper,
        'sport': sport
    }


def optimize_games_query(qs):
    """
    Applies query optimizations to the QuerySet.

    In the future, we will need to selectively choose what fields to select related, prefetch related on because qs
    can be for HockeyGames, BaseballGames, etc and the fields may not be common among those model classes.

    :param qs: QuerySet of games
    :return: The QuerySet with any query optimizations applied
    """
    return qs.select_related(
        'home_team',
        'home_team__division',
        'away_team',
        'away_team__division',
        'type',
        'location',
        'team'
    )


def get_games(sport, season, team=None):
    """
    Get games for the given sport and season. If a team is specified, the result will only include games for that team.

    :param sport: The sport to get games for, it is used to determine what model to use (HockeyGame, etc)
    :param season: Season to get games for
    :param team: Optional team to further narrow queryset down by
    :raises SportNotConfiguredException if the `sport` has not been configured
    :return: QuerySet of games for the given sport (HockeyGame, BaseballGame, etc)
    """
    model_cls = get_game_model_cls(sport)
    # Seasons are tied to leagues so we don't need to exclude games for other leagues
    qs = model_cls.objects.filter(season=season)
    if team is not None:
        qs = qs.filter(Q(home_team=team) | Q(away_team=team))
    return optimize_games_query(qs)


def get_game_list_view_context(user, sport, season, team=None):
    context = {}
    game_list_context = get_game_list_context(user, sport)
    games = get_games(sport, season, team=team)
    context.update({
        'active_tab': 'schedule',
        'season': season,
        'games': games,
        'has_games': games.exists()
    })
    context.update(game_list_context)
    return context
