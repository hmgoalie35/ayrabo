import re

from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.deprecation import MiddlewareMixin

from sports.models import SportRegistration
from userprofiles.models import UserProfile

regex = re.compile('/sport-registrations/\d+/(?P<role>(players|coaches|referees|managers))/create/?$')


class AccountAndSportRegistrationCompleteMiddleware(MiddlewareMixin):
    """
    This middleware makes sure the user has a profile, has at least one sport registration and has no sport
    registrations that are incomplete. Any requests to the urls in whitelisted_urls are allowed to pass through
    because a redirect loop would occur otherwise. It is the job of the view for the whitelisted_urls to make sure
    user's can't go from complete_registration_url to create_sport_registration_url, etc.
    """
    complete_registration_url = reverse_lazy('account_complete_registration')
    create_sport_registration_url = reverse_lazy('sportregistrations:create')
    whitelisted_urls = [reverse_lazy('account_logout'), complete_registration_url, create_sport_registration_url]

    def _is_whitelisted_url(self, path):
        if path in self.whitelisted_urls:
            return True
        return regex.match(path) is not None

    def process_request(self, request):
        # Allow debug toolbar requests so it works correctly and any request to admin for initial sport creation, etc.
        if '__debug__' in request.path or '/admin/' in request.path:  # pragma: no cover
            return None

        # Do not apply this middleware to anonymous users, or for any request to a whitelisted url. A redirect
        # loop would occur if we didn't whitelist certain urls.
        if request.user.is_authenticated and not self._is_whitelisted_url(request.path):

            up = UserProfile.objects.filter(user=request.user)
            if not up.exists():
                request.session['is_user_currently_registering'] = True
                return redirect(self.complete_registration_url)

            sport_registrations = SportRegistration.objects.filter(user=request.user)
            if not sport_registrations.exists():
                request.session['is_user_currently_registering'] = True
                return redirect(self.create_sport_registration_url)

            incomplete_sport_registrations = sport_registrations.filter(is_complete=False)
            if incomplete_sport_registrations.exists():
                iterator = incomplete_sport_registrations.iterator()
                sr = next(iterator, None)
                next_role_for_sr = sr.get_next_namespace_for_registration()
                next_sr = next(iterator, None)
                if next_sr is not None:
                    role = next_sr.get_next_namespace_for_registration()
                    request.session['next_sport_registration'] = {'id': next_sr.id, 'role': role}
                request.session['is_user_currently_registering'] = True
                url = 'sportregistrations:{role}:create'.format(role=next_role_for_sr)
                return redirect(reverse(url, kwargs={'pk': sr.id}))

            # At this point the user's account is "complete" and all sport registrations are complete
            request.session['is_user_currently_registering'] = False

            complete_sport_registrations = sport_registrations.filter(is_complete=True)
            user_roles = []
            for sport_reg in complete_sport_registrations:
                for role in sport_reg.roles:
                    user_roles.append(role) if role not in user_roles else None
            request.session['user_roles'] = user_roles
            return None

        return None
