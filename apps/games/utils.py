from django.db.models import Q

from ayrabo.utils import timedelta_to_hours_minutes_seconds
from games.mappings import get_game_model_cls
from games.models import AbstractGame
from users.authorizers import GameAuthorizer


def get_game_list_context(user, sport, games):
    """
    Computes common values used when listing games.

    :param user: User to get managers for
    :param sport: Only include managers for this sport
    :param games: List of games
    :return: Dict containing common values for listing games
    """
    game_authorizer = GameAuthorizer(user=user)
    game_authorizations = {}
    for game in games:
        game_authorizations.update({
            game.pk: {
                'can_user_update': game_authorizer.can_user_update(team=game.team),
                'can_user_update_game_rosters': game_authorizer.can_user_update_game_rosters(
                    home_team=game.home_team, away_team=game.away_team, sport=sport
                )
            }
        })

    return {
        'game_authorizations': game_authorizations,
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
        'home_team__organization',
        'away_team',
        'away_team__division',
        'away_team__organization',
        'type',
        'location',
        'team',
        'team__organization',
    )


def get_games(sport, season, team=None):
    """
    Get games for the given sport and season. If a team is specified, the result will only include games for that team.

    :param sport: The sport to get games for, it is used to determine what model to use (HockeyGame, etc)
    :param season: Season to get games for
    :param team: Optional team to further narrow queryset down by
    :raises SportNotConfiguredException: if the sport argument has not been configured
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
    games = get_games(sport, season, team=team)
    game_list_context = get_game_list_context(user, sport, games)
    context.update({
        'active_tab': 'schedule',
        'season': season,  # Note `get_team_detail_view_context` is also setting this context key to the same value.
        'games': games,
        'has_games': games.exists()
    })
    context.update(game_list_context)
    return context


def get_start_game_not_allowed_msg():
    _, minutes, _ = timedelta_to_hours_minutes_seconds(AbstractGame.START_GAME_GRACE_PERIOD)
    return f'Games can only be started {int(minutes)} minutes before the scheduled start time.'
