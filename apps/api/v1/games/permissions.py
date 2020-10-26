from rest_framework import permissions


class GamePlayerViewSetPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # The same permission check is used for the update game roster page, seems to fine to use the same check for the
        # api
        return view.game_authorizer.can_user_update_game_rosters(
            home_team=view.game.home_team,
            away_team=view.game.away_team,
            sport=view.sport
        )
