from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.deprecation import MiddlewareMixin

from userprofiles.models import UserProfile


class UserProfileCompleteMiddleware(MiddlewareMixin):
    """
    This middleware ensures the following:
        * The user has a profile
    Requests to any urls in whitelisted_urls are allowed to pass through to prevent redirect loops.
    """
    whitelisted_urls = [
        reverse_lazy('account_logout'),
        reverse_lazy('contact_us'),
        reverse_lazy('about_us')
    ]

    def _is_whitelisted_url(self, request):
        path = request.path
        # Also allow debug toolbar and admin panel requests through.
        return path in self.whitelisted_urls or '__debug__' in path or '/admin/' in path

    def process_request(self, request):
        """
        Returning `None` will allow the request to continue.
        """
        if request.user.is_anonymous or self._is_whitelisted_url(request):
            return None

        user_profile = UserProfile.objects.filter(user=request.user)
        if user_profile.exists():
            request.session['is_registration_complete'] = True
            return None

        redirect_url = reverse_lazy('account_complete_registration')
        request.session['is_registration_complete'] = False
        # Prevent redirect loop
        if redirect_url != request.path:
            site = get_current_site(request)
            msg = 'You must complete your account registration before browsing {}.'.format(site.domain)
            messages.warning(request, msg)
            return redirect(redirect_url)

        return None
