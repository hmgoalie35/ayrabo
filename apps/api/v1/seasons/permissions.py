from rest_framework import permissions

from managers.models import Manager
from scorekeepers.models import Scorekeeper


class SeasonRostersListPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        team = view._get_team()
        user = request.user
        sport = team.division.league.sport

        managers = Manager.objects.active().filter(team=team, user=user)
        scorekeepers = Scorekeeper.objects.active().filter(user=user, sport=sport)
        return managers.exists() or scorekeepers.exists()
