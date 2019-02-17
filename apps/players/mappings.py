from api.v1.players import serializers
from ayrabo.utils.exceptions import SportNotConfiguredException
from players import models


SPORT_PLAYER_MODEL_MAPPINGS = {
    'Ice Hockey': models.HockeyPlayer,
    'Basketball': models.BasketballPlayer,
    'Baseball': models.BaseballPlayer
}

SPORT_PLAYER_SERIALIZER_MAPPINGS = {
    'Ice Hockey': serializers.HockeyPlayerSerializer
}


def get_player_model_cls(sport, exception_cls=SportNotConfiguredException):
    """
    Fetch the appropriate player model class for the given sport. May be used by api views in which case the necessary
    API exception should be raised.

    :param sport: Sport that will be used to fetch the correct model class.
    :param exception_cls: Exception class to raise.
    :return: Player model class for the given sport.
    """
    model_cls = SPORT_PLAYER_MODEL_MAPPINGS.get(sport.name)
    if model_cls is None:
        raise exception_cls(sport)
    return model_cls


def get_player_serializer_cls(sport, exception_cls=SportNotConfiguredException):
    """
    Fetch the appropriate player serializer class for the given sport. May be used by api views in which case the
    necessary API exception should be raised.

    :param sport: Sport that will be used to fetch the correct model class.
    :param exception_cls: Exception class to raise.
    :return: Player serializer class for the given sport.
    """
    serializer_cls = SPORT_PLAYER_SERIALIZER_MAPPINGS.get(sport.name)
    if serializer_cls is None:
        raise exception_cls(sport)
    return serializer_cls
