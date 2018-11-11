from django.db.models import Q
from rest_framework import permissions

from managers.models import Manager
from scorekeepers.models import Scorekeeper


class GameRostersRetrieveUpdatePermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        sport = obj.team.division.league.sport
        managers = Manager.objects.active().filter(Q(team=obj.home_team) | Q(team=obj.away_team), user=user)
        scorekeepers = Scorekeeper.objects.active().filter(user=user, sport=sport)
        return managers.exists() or scorekeepers.exists()
