from managers.models import Manager
from users.models import Permission


class BaseAuthorizer(object):
    def __init__(self, user):
        self.user = user
        self.managers = None

    def _fetch_managers(self):
        if self.managers is None:
            self.managers = Manager.objects.active().filter(user=self.user)
        return self.managers

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
        self._fetch_managers()
        is_manager = self.managers.filter(team=team).exists()
        is_org_admin = self.user.has_object_permission(Permission.ADMIN, team.organization)
        return is_manager or is_org_admin
