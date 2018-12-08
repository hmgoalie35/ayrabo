from ayrabo.utils import chunk
from games.mappings import get_game_model_cls
from games.utils import get_game_list_context, optimize_games_query


def get_chunked_divisions(divisions, per_row=4):
    # The generator gets exhausted after the first iteration over the items. Convert to a list here to prevent this
    # problem.
    return list(chunk(divisions, per_row))


def get_games(sport, season):
    model_cls = get_game_model_cls(sport)
    # Seasons are tied to leagues so we don't need to exclude games for other leagues
    qs = model_cls.objects.filter(season=season)
    return optimize_games_query(qs)


def get_schedule_view_context(user, sport, season):
    context = {}
    game_list_context = get_game_list_context(user, sport)
    games = get_games(sport, season)
    context.update({
        'active_tab': 'schedule',
        'season': season,
        'games': games,
        'has_games': games.count() > 0
    })
    context.update(game_list_context)
    return context
