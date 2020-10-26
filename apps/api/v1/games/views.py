from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from api.exceptions import SportNotConfiguredAPIException
from api.mixins import BulkCreateMixin, BulkDeleteMixin, BulkUpdateMixin, BulkViewActionMixin
from games.mappings import get_game_model_cls, get_game_player_model_cls, get_game_player_serializer_cls
from sports.models import Sport
from users.authorizers import GameAuthorizer
from .permissions import GamePlayerViewSetPermission


class GamePlayerViewSet(BulkViewActionMixin,
                        BulkCreateMixin,
                        BulkUpdateMixin,
                        BulkDeleteMixin,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    API for game players (aka game rosters)
    """
    permission_classes = (IsAuthenticated, GamePlayerViewSetPermission)

    def _get_sport(self):
        if hasattr(self, 'sport'):
            return self.sport
        self.sport = get_object_or_404(Sport, pk=self.kwargs.get('pk'))
        return self.sport

    def _get_game(self):
        if hasattr(self, 'game'):
            return self.game
        model_cls = get_game_model_cls(self.sport, exception_cls=SportNotConfiguredAPIException)
        self.game = get_object_or_404(
            model_cls.objects.select_related(
                'home_team',
                'home_team__organization',
                'away_team',
                'away_team__organization'
            ),
            pk=self.kwargs.get('game_pk')
        )
        return self.game

    def initial(self, request, *args, **kwargs):
        # DRF doesn't call django's `setup` (might be a bug, idk) so we need to override `initial` so the permission
        # class has access to the sport, game and game authorizer. Would rather not set attrs of the view in the
        # permission class so we do it here
        self._get_sport()
        self._get_game()
        self.game_authorizer = GameAuthorizer(user=self.request.user)
        super().initial(request, *args, **kwargs)

    def get_serializer_class(self):
        return get_game_player_serializer_cls(self.sport, self.action)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        can_update_game = self.game.can_update()
        context.update({
            'can_update_home_roster': can_update_game and self.game_authorizer.can_user_update_game_roster(
                team=self.game.home_team, sport=self.sport
            ),
            'can_update_away_roster': can_update_game and self.game_authorizer.can_user_update_game_roster(
                team=self.game.away_team, sport=self.sport
            ),
            'game': self.game,
            'sport': self.sport,
        })
        return context

    def get_queryset(self):
        model_cls = get_game_player_model_cls(self.sport)
        # Return objs for one of the AbstractGamePlayer model subclasses
        return model_cls.objects.select_related('team', 'game', 'player').filter(game=self.game)
