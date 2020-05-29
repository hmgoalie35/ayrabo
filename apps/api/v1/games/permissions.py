from rest_framework import permissions


class GameRostersRetrieveUpdatePermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return view.game_authorizer.can_user_update_game_rosters(
            home_team=obj.home_team,
            away_team=obj.away_team,
            sport=view.sport
        )
