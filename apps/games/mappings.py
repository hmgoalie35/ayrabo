from api.exceptions import SportNotConfiguredAPIException
from api.v1.games.serializers import (
    HockeyGamePlayerBulkCreateSerializer,
    HockeyGamePlayerBulkDeleteSerializer,
    HockeyGamePlayerBulkUpdateSerializer,
    HockeyGamePlayerSerializer,
)
from ayrabo.utils.exceptions import SportNotConfiguredException
from games.forms import HockeyGameCreateForm, HockeyGameScoresheetForm, HockeyGameUpdateForm
from games.models import HockeyGame, HockeyGamePlayer


# Forms
SPORT_GAME_CREATE_FORM_MAPPINGS = {
    'Ice Hockey': HockeyGameCreateForm,
}

SPORT_GAME_UPDATE_FORM_MAPPINGS = {
    'Ice Hockey': HockeyGameUpdateForm,
}

SPORT_GAME_SCORESHEET_FORM_MAPPINGS = {
    'Ice Hockey': HockeyGameScoresheetForm,
}

# Models
SPORT_GAME_MODEL_MAPPINGS = {
    'Ice Hockey': HockeyGame,
}

SPORT_GAME_PLAYER_MODEL_MAPPINGS = {
    'ice-hockey': HockeyGamePlayer,
}

# Serializers
SPORT_GAME_PLAYER_SERIALIZER_CLASS_MAPPINGS = {
    'ice-hockey': HockeyGamePlayerSerializer,
}

SPORT_GAME_PLAYER_BULK_CREATE_SERIALIZER_CLASS_MAPPINGS = {
    'ice-hockey': HockeyGamePlayerBulkCreateSerializer,
}

SPORT_GAME_PLAYER_BULK_UPDATE_SERIALIZER_CLASS_MAPPINGS = {
    'ice-hockey': HockeyGamePlayerBulkUpdateSerializer,
}

SPORT_GAME_PLAYER_BULK_DELETE_SERIALIZER_CLASS_MAPPINGS = {
    'ice-hockey': HockeyGamePlayerBulkDeleteSerializer,
}


def get_game_model_cls(sport, exception_cls=SportNotConfiguredException):
    model_cls = SPORT_GAME_MODEL_MAPPINGS.get(sport.name)
    if model_cls is None:
        raise exception_cls(sport)
    return model_cls


def get_game_create_form_cls(sport):
    form_cls = SPORT_GAME_CREATE_FORM_MAPPINGS.get(sport.name)
    if form_cls is None:
        raise SportNotConfiguredException(sport)
    return form_cls


def get_game_update_form_cls(sport):
    form_cls = SPORT_GAME_UPDATE_FORM_MAPPINGS.get(sport.name)
    if form_cls is None:
        raise SportNotConfiguredException(sport)
    return form_cls


def get_game_scoresheet_form_cls(sport):
    form_cls = SPORT_GAME_SCORESHEET_FORM_MAPPINGS.get(sport.name)
    if form_cls is None:
        raise SportNotConfiguredException(sport)
    return form_cls


def get_game_player_serializer_cls_mappings(action):
    mappings = {
        'bulk_create': SPORT_GAME_PLAYER_BULK_CREATE_SERIALIZER_CLASS_MAPPINGS,
        'bulk_update': SPORT_GAME_PLAYER_BULK_UPDATE_SERIALIZER_CLASS_MAPPINGS,
        'bulk_delete': SPORT_GAME_PLAYER_BULK_DELETE_SERIALIZER_CLASS_MAPPINGS
    }
    return mappings.get(action, SPORT_GAME_PLAYER_SERIALIZER_CLASS_MAPPINGS)


def get_game_player_serializer_cls(sport, action):
    mappings = get_game_player_serializer_cls_mappings(action)
    serializer_cls = mappings.get(sport.slug)
    if serializer_cls is None:
        raise SportNotConfiguredAPIException(sport)
    return serializer_cls


def get_game_player_model_cls(sport, exception_cls=SportNotConfiguredException):
    model_cls = SPORT_GAME_PLAYER_MODEL_MAPPINGS.get(sport.slug)
    if model_cls is None:
        raise exception_cls(sport)
    return model_cls
