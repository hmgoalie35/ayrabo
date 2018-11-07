from ayrabo.utils.exceptions import SportNotConfiguredException
from games.forms import HockeyGameCreateForm, HockeyGameUpdateForm
from games.models import HockeyGame


SPORT_GAME_CREATE_FORM_MAPPINGS = {
    'Ice Hockey': HockeyGameCreateForm
}

SPORT_GAME_UPDATE_FORM_MAPPINGS = {
    'Ice Hockey': HockeyGameUpdateForm
}

SPORT_GAME_MODEL_MAPPINGS = {
    'Ice Hockey': HockeyGame
}


def get_game_model_cls(sport):
    model_cls = SPORT_GAME_MODEL_MAPPINGS.get(sport.name)
    if model_cls is None:
        raise SportNotConfiguredException(sport)
    return model_cls
