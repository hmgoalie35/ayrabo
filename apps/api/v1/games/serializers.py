from django.db.models import Q
from rest_framework import serializers

from api.exceptions import SportNotConfiguredAPIException
from api.serializers import (
    AbstractBulkCreateModelSerializer,
    AbstractBulkDeleteModelSerializer,
    AbstractBulkUpdateModelSerializer,
)
from games.models import HockeyGamePlayer
from teams.models import Team


class AbstractGamePlayerCreateSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        from games.mappings import get_game_model_cls
        from players.mappings import get_player_model_cls

        super().__init__(*args, **kwargs)
        sport = self.context.get('sport')
        game = self.context.get('game')

        game_model_cls = get_game_model_cls(sport, exception_cls=SportNotConfiguredAPIException)
        player_model_cls = get_player_model_cls(sport, exception_cls=SportNotConfiguredAPIException)
        home_team = game.home_team
        away_team = game.away_team

        self.fields['team'].queryset = Team.objects.filter(Q(id=home_team.id) | Q(id=away_team.id))
        # Making these fields dynamic requires digging deep into drf, not worth the effort
        self.fields['game'].queryset = game_model_cls.objects.filter(id=game.id)
        self.fields['player'].queryset = player_model_cls.objects.active().select_related('user').filter(
            Q(team=home_team) | Q(team=away_team)
        )

    def validate(self, attrs):
        err_msg = 'You do not have permission to manage game players for this team.'

        game = self.context.get('game')
        team = attrs.get('team')
        team_id = team.id
        home_team_id = game.home_team_id
        away_team_id = game.away_team_id
        player = attrs.get('player')
        can_update_home_roster = self.context.get('can_update_home_roster')
        can_update_away_roster = self.context.get('can_update_away_roster')

        # Make sure the user is authorized to update the game roster for the given team
        # It doesn't make sense for both of these if clauses to execute but should be fine to keep it like this
        if team_id == home_team_id and not can_update_home_roster:
            raise serializers.ValidationError({'team': err_msg})
        if team_id == away_team_id and not can_update_away_roster:
            raise serializers.ValidationError({'team': err_msg})

        # Make sure the player actually belongs to the given team
        if player.team_id != team_id:
            raise serializers.ValidationError({'player': 'Player does not belong to the specified team.'})

        return attrs

    class Meta:
        # Subclasses should include all fields referenced above in the `fields = (...)` variable
        pass


class HockeyGamePlayerSerializer(serializers.ModelSerializer):
    """
    Basic serializer that should only be used for listing. To support single create, etc please look at the validation
    logic the abstract game player bulk create serializer is doing.
    """

    class Meta:
        model = HockeyGamePlayer
        fields = ('id', 'team', 'is_starting', 'game', 'player')


class HockeyGamePlayerBulkCreateSerializer(AbstractGamePlayerCreateSerializer, AbstractBulkCreateModelSerializer):
    class Meta(AbstractBulkCreateModelSerializer.Meta):
        model = HockeyGamePlayer
        # Game will likely be available to us (since it is present in the url) but omitting here means we don't get the
        # validation for unique constraint (b/w game & player) violations. Might as well just include game here and have
        # the client send it
        fields = ('id', 'team', 'is_starting', 'game', 'player')


# TODO check user authorized to update game player(s) for the provided team(s)
class HockeyGamePlayerBulkUpdateSerializer(AbstractBulkUpdateModelSerializer):
    class Meta(AbstractBulkUpdateModelSerializer.Meta):
        model = HockeyGamePlayer
        fields = ('id', 'is_starting')


# TODO check user authorized to delete game player(s) for the provided team(s)
class HockeyGamePlayerBulkDeleteSerializer(AbstractBulkDeleteModelSerializer):
    class Meta(AbstractBulkDeleteModelSerializer.Meta):
        model = HockeyGamePlayer
