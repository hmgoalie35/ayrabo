from django.contrib.contenttypes.models import ContentType
from django.utils.functional import cached_property

from managers.models import Manager
from organizations.models import Organization
from scorekeepers.models import Scorekeeper
from users.models import Permission


class BaseAuthorizer(object):
    def __init__(self, user):
        self.user = user

    @cached_property
    def manager_team_ids(self):
        """
        Compute team ids the user is an active manager for.

        As of now It is way less queries to check if an id is in a list of ids over calling queryset methods and
        triggering db queries.

        :return: QuerySet of team ids
        """
        return Manager.objects.active().filter(user=self.user).values_list('team_id', flat=True)

    @cached_property
    def org_admin_org_ids(self):
        """
        Compute org ids the user is an org admin for.

        As of now It is way less queries to check if an id is in a list of ids over calling queryset methods and
        triggering db queries.

        :return: QuerySet of organization ids
        """
        return Permission.objects.filter(
            user=self.user,
            name=Permission.ADMIN,
            content_type=ContentType.objects.get_for_model(model=Organization)
        ).values_list('object_id', flat=True)

    @cached_property
    def scorekeeper_sport_ids(self):
        """
        Compute sport ids the user is an active scorekeeper for.

        As of now It is way less queries to check if an id is in a list of ids over calling queryset methods and
        triggering db queries.

        :return: QuerySet of sport ids
        """
        return Scorekeeper.objects.active().filter(user=self.user).values_list('sport_id', flat=True)

    def _is_manager_for_team(self, team):
        return team.id in self.manager_team_ids

    def _is_org_admin_for_org(self, organization):
        return organization.id in self.org_admin_org_ids

    def _is_scorekeeper_for_sport(self, sport):
        return sport.id in self.scorekeeper_sport_ids

    def can_user_create(self, *args, **kwargs):
        return False

    def can_user_retrieve(self, *args, **kwargs):
        return False

    def can_user_update(self, *args, **kwargs):
        return False

    def can_user_delete(self, *args, **kwargs):
        return False

    def can_user_list(self, *args, **kwargs):
        return False


class GameAuthorizer(BaseAuthorizer):

    def can_user_create(self, team, *args, **kwargs):
        return self._is_manager_for_team(team=team) or self._is_org_admin_for_org(organization=team.organization)

    def can_user_update(self, team, *args, **kwargs):
        return self.can_user_create(team=team)

    def can_user_update_game_roster(self, team, sport):
        """
        Determine if the user can actually update the game roster for a team. A user may be able to update the game
        roster for the home team but not the away team, for example.
        """
        is_manager = self._is_manager_for_team(team=team)
        is_org_admin = self._is_org_admin_for_org(organization=team.organization)
        is_scorekeeper = self._is_scorekeeper_for_sport(sport=sport)
        return is_manager or is_org_admin or is_scorekeeper

    def can_user_update_game_rosters(self, home_team, away_team, sport, *args, **kwargs):
        """
        Determine if the user can actually navigate to the game rosters update page (if links should be shown to them)
        """
        return (
            self.can_user_update_game_roster(team=home_team, sport=sport) or
            self.can_user_update_game_roster(team=away_team, sport=sport)
        )

    def can_user_take_score(self, game, sport, *args, **kwargs):
        return (
            game.can_initialize() and
            self.can_user_update_game_rosters(game.home_team, game.away_team, sport, *args, **kwargs)
        )


class SeasonRosterAuthorizer(BaseAuthorizer):
    def can_user_create(self, team, *args, **kwargs):
        is_manager = self._is_manager_for_team(team=team)
        is_org_admin = self._is_org_admin_for_org(organization=team.organization)
        return is_manager or is_org_admin

    def can_user_update(self, team, *args, **kwargs):
        return self.can_user_create(team=team)

    def can_user_list(self, team, sport, api=False, *args, **kwargs):
        """
        The season roster list api view allows scorekeepers to list (due to game roster update page listing season
        rosters).
        """
        can_user_create = self.can_user_create(team, sport)
        if api:
            is_scorekeeper = self._is_scorekeeper_for_sport(sport=sport)
            return can_user_create or is_scorekeeper
        return can_user_create
