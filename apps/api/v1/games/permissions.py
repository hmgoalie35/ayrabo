from django.db.models import Q
from rest_framework import permissions

from managers.models import Manager
from scorekeepers.models import Scorekeeper


class GameRostersRetrieveUpdatePermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        sport = obj.team.division.league.sport

        # TODO DRY this out. Move to `can_user_update` function on game. In order to prevent duplicating these queries
        # in get_context_data (for normal views) the function can return (result, managers, scorekeepers, ...etc)
        managers = Manager.objects.active().filter(Q(team=obj.home_team) | Q(team=obj.away_team), user=user)
        scorekeepers = Scorekeeper.objects.active().filter(user=user, sport=sport)
        return managers.exists() or scorekeepers.exists()
