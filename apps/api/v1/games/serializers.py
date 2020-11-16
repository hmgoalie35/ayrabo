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


def validate_user_authorized_to_manage_team(team, game, context):
    """
    Validate the user is authorized to manage game players for the specified team.
    """
    err_msg = 'You do not have permission to manage game players for this team.'

    team_id = team.id
    home_team_id = game.home_team_id
    away_team_id = game.away_team_id
    can_update_home_roster = context.get('can_update_home_roster')
    can_update_away_roster = context.get('can_update_away_roster')
    # Could just return one huge clause here bit I figured this is a little easier to reason about/unit test
    if team_id == home_team_id and can_update_home_roster:
        return True
    if team_id == away_team_id and can_update_away_roster:
        return True
    # I think it's better design to default to raising an exception
    raise serializers.ValidationError({'team': err_msg})


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
        team = attrs.get('team')
        game = self.context.get('game')
        team_id = team.id
        player = attrs.get('player')

        validate_user_authorized_to_manage_team(team, game, self.context)

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


class HockeyGamePlayerBulkUpdateSerializer(AbstractBulkUpdateModelSerializer):
    def validate(self, attrs):
        super().validate(attrs)
        instance = attrs.get('id')
        team = instance.team
        game = instance.game

        validate_user_authorized_to_manage_team(team, game, self.context)

        return attrs

    class Meta(AbstractBulkUpdateModelSerializer.Meta):
        model = HockeyGamePlayer
        fields = ('id', 'is_starting')


class HockeyGamePlayerBulkDeleteSerializer(AbstractBulkDeleteModelSerializer):
    def validate(self, attrs):
        instance = attrs.get('id')
        team = instance.team
        game = instance.game

        validate_user_authorized_to_manage_team(team, game, self.context)

        return attrs

    class Meta(AbstractBulkDeleteModelSerializer.Meta):
        model = HockeyGamePlayer
