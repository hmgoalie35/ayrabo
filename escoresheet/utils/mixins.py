from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.urls import reverse

from sports.models import SportRegistration
from userprofiles.models import UserProfile


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


class AccountAndSportRegistrationCompleteMixin(object):
    """
    A mixin that does the same thing as the middleware, but because the middleware lets the whitelisted
    urls through, we need to do the check again in the actual view.
    """

    def dispatch(self, request, *args, **kwargs):
        redirect_url = None
        up = UserProfile.objects.filter(user=request.user)
        sport_registrations = SportRegistration.objects.filter(user=request.user)
        incomplete_sport_registrations = sport_registrations.filter(is_complete=False)

        if not up.exists():
            request.session['is_user_currently_registering'] = True
            redirect_url = reverse('account_complete_registration')
        elif not sport_registrations.exists():
            request.session['is_user_currently_registering'] = True
            redirect_url = reverse('sportregistrations:create')
        elif incomplete_sport_registrations.exists():
            request.session['is_user_currently_registering'] = True
            sr = incomplete_sport_registrations.first()
            # TODO Figure out a better way to do this, it seems really inefficient to run this on every request.
            # Add boolean fields to sport reg model for is_player_complete, etc.
            next_role = None
            related_objects = sr.get_related_role_objects()
            if sr.has_role('Player') and related_objects.get('Player') is None:
                next_role = 'players'
            elif sr.has_role('Coach') and related_objects.get('Coach') is None:
                next_role = 'coaches'
            elif sr.has_role('Referee') and related_objects.get('Referee') is None:
                next_role = 'referees'
            elif sr.has_role('Manager') and related_objects.get('Manager') is None:
                next_role = 'managers'
            url = 'sportregistrations:{role}:create'.format(role=next_role)
            redirect_url = reverse(url, kwargs={'pk': sr.id})

        if redirect_url is not None and request.path != redirect_url:
            return redirect(redirect_url)

        if redirect_url is None:
            request.session['is_user_currently_registering'] = False
        # Don't need to add `user_roles` to the session because the middleware will be called on the
        # next request regardless.
        return super(AccountAndSportRegistrationCompleteMixin, self).dispatch(request, *args, **kwargs)
