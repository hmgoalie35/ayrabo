from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.exceptions import SportNotConfiguredAPIException
from api.v1.games.serializers import HockeyGameSerializer
from games import mappings
from games.models import HockeyGame
from games.utils import optimize_games_query
from managers.models import Manager
from scorekeepers.models import Scorekeeper
from seasons.models import Season
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


class F(filters.FilterSet):
    season = filters.ModelChoiceFilter(queryset=Season.objects.all(), required=True)

    class Meta:
        model = HockeyGame
        fields = ('season',)


class GameListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = HockeyGameSerializer
    queryset = HockeyGame.objects.all()
    # Only seasons for requested league should be allowed to be filtered by
    # filterset_fields = ('season',)
    # filterset_class = F

    def _get_sport(self):
        return get_object_or_404(Sport, pk=self.kwargs.get('pk'))

    def get_serializer_class(self):
        return self.serializer_class

    def get_queryset(self):
        qs = super().get_queryset()
        # Would need to check query params here, filter qs by season query param (which isn't the best. Better practice
        # to just have season pk in url /api/v1/sports/:id/seasons/:season_pk/games)
        qs = qs.filter(season_id=1)
        return optimize_games_query(qs)
