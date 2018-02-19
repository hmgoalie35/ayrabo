from api.v1.players import serializers
from players import models

SPORT_PLAYER_MODEL_MAPPINGS = {
    'Ice Hockey': models.HockeyPlayer,
    'Basketball': models.BasketballPlayer,
    'Baseball': models.BaseballPlayer
}

SPORT_PLAYER_SERIALIZER_MAPPINGS = {
    'Ice Hockey': serializers.HockeyPlayerSerializer
}
