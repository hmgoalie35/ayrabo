from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.exceptions import SportNotConfiguredAPIException
from players.mappings import get_player_model_cls, get_player_serializer_cls
from teams.models import Team


class PlayersListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('is_active',)

    def _get_team(self):
        if hasattr(self, 'team'):  # pragma: no cover
            return self.team
        self.team = get_object_or_404(
            Team.objects.select_related('division', 'division__league', 'division__league__sport'),
            pk=self.kwargs.get('pk'))
        self.sport = self.team.division.league.sport
        return self.team

    def get_serializer_class(self):
        return get_player_serializer_cls(self.sport, exception_cls=SportNotConfiguredAPIException)

    def get_queryset(self):
        team = self._get_team()
        model_cls = get_player_model_cls(self.sport, exception_cls=SportNotConfiguredAPIException)
        return model_cls.objects.filter(team=team).select_related('user')
