from rest_framework import permissions

from users.authorizers import SeasonRosterAuthorizer


class SeasonRostersListPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        season_roster_authorizer = SeasonRosterAuthorizer(user=request.user)
        team = view._get_team()
        sport = team.division.league.sport
        return season_roster_authorizer.can_user_list(team=team, sport=sport)
