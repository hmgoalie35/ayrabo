from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.urls import reverse

from sports.models import SportRegistration


class UserHasRolesMixin(object):
    """
    A mixin that makes sure the current user has the appropriate roles.

    i.e. That a user who is a coach actually has the coach role.
    """
    roles_to_check = []
    user_has_no_role_msg = 'You do not have permission to perform this action.'

    def dispatch(self, request, *args, **kwargs):
        assert isinstance(self.roles_to_check, list)
        roles_set = set(self.roles_to_check)
        if roles_set and roles_set <= set(SportRegistration.ROLES):
            if not roles_set <= set(request.session.get('user_roles', [])):
                messages.error(request, self.user_has_no_role_msg)
                return redirect(reverse('home'))
        else:
            raise ImproperlyConfigured('The value of roles_to_check must be specified on the view class, '
                                       'or you have specified values not in {}'.format(SportRegistration.ROLES))
        return super(UserHasRolesMixin, self).dispatch(request, *args, **kwargs)
