from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.exceptions import SportNotConfiguredAPIException
from ayrabo.utils.mappings import SPORT_PLAYER_MODEL_MAPPINGS, SPORT_PLAYER_SERIALIZER_MAPPINGS
from teams.models import Team


class PlayersListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    filter_fields = ('is_active',)

    def _get_team(self):
        if hasattr(self, 'team'):  # pragma: no cover
            return self.team
        self.team = get_object_or_404(
            Team.objects.select_related('division', 'division__league', 'division__league__sport'),
            pk=self.kwargs.get('pk'))
        self.sport = self.team.division.league.sport
        return self.team

    def get_serializer_class(self):
        serializer_cls = SPORT_PLAYER_SERIALIZER_MAPPINGS.get(self.sport.name)
        if serializer_cls is None:
            raise SportNotConfiguredAPIException(self.sport)
        return serializer_cls

    def get_queryset(self):
        team = self._get_team()
        model_cls = SPORT_PLAYER_MODEL_MAPPINGS.get(self.sport.name)
        if model_cls is None:
            raise SportNotConfiguredAPIException(self.sport)
        return model_cls.objects.filter(team=team).select_related('user')
