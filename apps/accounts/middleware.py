from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.deprecation import MiddlewareMixin

from sports.models import SportRegistration
from userprofiles.models import UserProfile


class AccountAndSportRegistrationCompleteMiddleware(MiddlewareMixin):
    """
    This middleware makes sure the user has a profile, has at least one sport registration and has no sport
    registrations that are incomplete. Any requests to the urls in whitelisted_urls are allowed to pass through
    because a redirect loop would occur otherwise.
    """
    whitelisted_urls = [
        reverse_lazy('account_logout'),
        reverse_lazy('contact_us'),
        reverse_lazy('about_us')
    ]

    def _is_whitelisted_url(self, path):
        # Allow debug toolbar requests so it works correctly and any request to admin for initial sport creation, etc.
        return path in self.whitelisted_urls or '__debug__' in path or '/admin/' in path

    def process_request(self, request):
        # Only apply this middleware to authenticated users not requesting a whitelisted url. A redirect loop would
        # occur otherwise.
        if request.user.is_authenticated and not self._is_whitelisted_url(request.path):
            redirect_url = None
            user_profile = UserProfile.objects.filter(user=request.user)
            sport_registrations = SportRegistration.objects.filter(user=request.user)
            incomplete_sport_registrations = sport_registrations.filter(is_complete=False)
            request.session['is_user_currently_registering'] = True

            if not user_profile.exists():
                redirect_url = reverse_lazy('account_complete_registration')
            elif not sport_registrations.exists():
                redirect_url = reverse_lazy('sportregistrations:create')
            elif incomplete_sport_registrations.exists():
                iterator = incomplete_sport_registrations.iterator()
                sr = next(iterator, None)
                next_role_for_sr = sr.get_next_namespace_for_registration()
                next_sr = next(iterator, None)
                if next_sr is not None:
                    role = next_sr.get_next_namespace_for_registration()
                    request.session['next_sport_registration'] = {'id': next_sr.id, 'role': role}
                url = 'sportregistrations:{role}:create'.format(role=next_role_for_sr)
                redirect_url = reverse_lazy(url, kwargs={'pk': sr.id})

            if redirect_url is None:
                # At this point the user's account is "complete" and all sport registrations are complete
                request.session['is_user_currently_registering'] = False

                complete_sport_registrations = sport_registrations.filter(is_complete=True)
                user_roles = []
                for sport_reg in complete_sport_registrations:
                    for role in sport_reg.roles:
                        user_roles.append(role) if role not in user_roles else None
                request.session['user_roles'] = user_roles
                return None
            elif redirect_url != request.path:
                return redirect(redirect_url)
        return None
