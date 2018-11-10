from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.exceptions import SportNotConfiguredAPIException
from seasons.models import HockeySeasonRoster
from teams.models import Team
from .permissions import SeasonRostersListPermission
from .serializers import HockeySeasonRosterSerializer

SPORT_SEASON_ROSTER_SERIALIZER_MAPPINGS = {
    'Ice Hockey': HockeySeasonRosterSerializer,
}

SPORT_SEASON_ROSTER_MODEL_MAPPINGS = {
    'Ice Hockey': HockeySeasonRoster,
}


class SeasonRostersListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, SeasonRostersListPermission)
    filterset_fields = ('season',)

    def _get_team(self):
        if hasattr(self, 'team'):
            return self.team
        self.team = get_object_or_404(
            Team.objects.select_related('division', 'division__league', 'division__league__sport'),
            pk=self.kwargs.get('pk')
        )
        self.sport = self.team.division.league.sport
        return self.team

    def get_serializer_class(self):
        serializer_cls = SPORT_SEASON_ROSTER_SERIALIZER_MAPPINGS.get(self.sport.name)
        if serializer_cls is None:
            raise SportNotConfiguredAPIException(self.sport)
        return serializer_cls

    def get_queryset(self):
        team = self._get_team()
        model_cls = SPORT_SEASON_ROSTER_MODEL_MAPPINGS.get(self.sport.name)
        if model_cls is None:
            raise SportNotConfiguredAPIException(self.sport)
        return model_cls.objects.filter(team=team).prefetch_related('players__user')
