from django.core import exceptions
from rest_framework import serializers

from games.models import HockeyGame
from players.models import HockeyPlayer


class AbstractGameRosterSerializer(serializers.ModelSerializer):
    player_model_cls = None

    def __init__(self, instance, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        if self.player_model_cls is None:
            raise exceptions.ImproperlyConfigured('You need to specify player_model_cls.')

        home_team = instance.home_team
        away_team = instance.away_team

        # This prevents players from other teams, divisions, leagues from being added to the roster. If this serializer
        # isn't used to add players, it is possible the player will be successfully added but the api endpoint won't
        # include that player.
        qs = self.player_model_cls.objects.active().select_related('user')
        self.fields['home_players'] = serializers.PrimaryKeyRelatedField(many=True, queryset=qs.filter(team=home_team),
                                                                         label='Home Roster')
        self.fields['away_players'] = serializers.PrimaryKeyRelatedField(many=True, queryset=qs.filter(team=away_team),
                                                                         label='Away Roster')

    def validate_home_players(self, value):
        # TODO Only allow scorekeeper or home manager to update home players.
        return value

    def validate_away_players(self, value):
        return value

    class Meta:
        model = None
        fields = ('home_players', 'away_players')


class HockeyGameRosterSerializer(AbstractGameRosterSerializer):
    player_model_cls = HockeyPlayer

    class Meta(AbstractGameRosterSerializer.Meta):
        model = HockeyGame
