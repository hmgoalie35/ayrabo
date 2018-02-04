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
