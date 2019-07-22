from django.core import exceptions
from rest_framework import serializers

from games.models import HockeyGame
from players.models import HockeyPlayer


class AbstractGameRosterSerializer(serializers.ModelSerializer):
    player_model_cls = None
    not_permitted_msg = 'You do not have permission to perform this action.'

    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        if self.player_model_cls is None:  # pragma: no cover
            raise exceptions.ImproperlyConfigured('You need to specify player_model_cls.')

        if instance:
            # This prevents players from other teams, divisions, leagues from being added to the roster. If this
            # serializer isn't used to add players, it is possible the player will be successfully added but the api
            # endpoint won't include that player.
            qs = self.player_model_cls.objects.active().select_related('user')
            home_players = qs.filter(team=instance.home_team)
            away_players = qs.filter(team=instance.away_team)
        else:
            empty_qs = self.player_model_cls.objects.none()
            home_players = empty_qs
            away_players = empty_qs

        self.fields['home_players'] = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=home_players,
            label='Home Roster'
        )
        self.fields['away_players'] = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=away_players,
            label='Away Roster'
        )

    def validate_home_players(self, value):
        if not self.context.get('can_update_home_roster'):
            raise serializers.ValidationError(self.not_permitted_msg)
        return value

    def validate_away_players(self, value):
        if not self.context.get('can_update_away_roster'):
            raise serializers.ValidationError(self.not_permitted_msg)
        return value

    class Meta:
        model = None
        fields = ('home_players', 'away_players')


class HockeyGameRosterSerializer(AbstractGameRosterSerializer):
    player_model_cls = HockeyPlayer

    class Meta(AbstractGameRosterSerializer.Meta):
        model = HockeyGame
