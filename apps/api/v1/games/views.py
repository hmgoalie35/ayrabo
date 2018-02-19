from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.exceptions import SportNotConfiguredAPIException
from games import mappings
from managers.models import Manager
from scorekeepers.models import Scorekeeper
from sports.models import Sport
from . import serializers
from .permissions import GameRostersRetrieveUpdatePermission

SPORT_SERIALIZER_CLASS_MAPPINGS = {
    'Ice Hockey': serializers.HockeyGameRosterSerializer
}


class GameRostersRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, GameRostersRetrieveUpdatePermission)
    lookup_url_kwarg = 'game_pk'

    def _get_sport(self):
        if hasattr(self, 'sport'):
            return self.sport
        self.sport = get_object_or_404(Sport, pk=self.kwargs.get('pk'))
        return self.sport

    def get_object(self):
        if hasattr(self, 'instance'):
            return self.instance
        self.instance = super().get_object()
        return self.instance

    def get_serializer_context(self):
        context = super().get_serializer_context()
        obj = self.get_object()
        user = self.request.user
        managers = Manager.objects.active().filter(user=user)
        scorekeepers = Scorekeeper.objects.active().filter(user=user, sport=self.sport)
        context['can_update_home_roster'] = managers.filter(team=obj.home_team).exists() or scorekeepers.exists()
        context['can_update_away_roster'] = managers.filter(team=obj.away_team).exists() or scorekeepers.exists()
        return context

    def get_serializer_class(self):
        serializer_cls = SPORT_SERIALIZER_CLASS_MAPPINGS.get(self.sport.name)
        if serializer_cls is None:
            raise SportNotConfiguredAPIException(self.sport)

        return serializer_cls

    def get_queryset(self):
        sport = self._get_sport()
        model_cls = mappings.SPORT_GAME_MODEL_MAPPINGS.get(sport.name)
        if model_cls is None:
            raise SportNotConfiguredAPIException(sport)

        # FYI This view deals w/ the various game models
        return model_cls.objects.all().select_related(
            'home_team', 'away_team', 'team', 'team__division', 'team__division__league',
            'team__division__league__sport').prefetch_related('home_players', 'home_players__user', 'away_players',
                                                              'away_players__user')
