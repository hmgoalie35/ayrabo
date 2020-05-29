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
    def _is_manager_for_team(self, team):
        return team.id in self.manager_team_ids

    def _is_org_admin_for_org(self, organization):
        return organization.id in self.org_admin_org_ids

    def _is_scorekeeper_for_sport(self, sport):
        return sport.id in self.scorekeeper_sport_ids

    def can_user_create(self, team, *args, **kwargs):
        return self._is_manager_for_team(team=team) or self._is_org_admin_for_org(organization=team.organization)

    def can_user_update(self, team, *args, **kwargs):
        return self.can_user_create(team=team)

    def can_user_update_game_rosters(self, home_team, away_team, sport, *args, **kwargs):
        is_manager = self._is_manager_for_team(team=home_team) or self._is_manager_for_team(team=away_team)
        is_org_admin = (
            self._is_org_admin_for_org(organization=home_team.organization) or
            self._is_org_admin_for_org(organization=away_team.organization)
        )
        is_scorekeeper = self._is_scorekeeper_for_sport(sport=sport)
        return is_manager or is_org_admin or is_scorekeeper
