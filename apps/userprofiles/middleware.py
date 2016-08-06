from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from userprofiles.models import UserProfile


class UserProfileCreatedMiddleware(object):
    """
    This middleware makes sure a user has created a userprofile.
    """

    def process_request(self, request):
        create_profile_url = reverse('profile:create')
        whitelisted_urls = [reverse('account_logout'), create_profile_url]

        # debug_toolbar wasn't working properly because of my custom middleware so let all debug_toolbar
        # requests through
        if '__debug__' in request.path:
            return None

        # Do not apply this middleware to anonymous users, or for any request to a whitelisted url. An infinite redirect
        # loop would occur if create_profile_url weren't whitelisted
        if request.user.is_authenticated() and request.path not in whitelisted_urls:
            up = UserProfile.objects.filter(user=request.user)
            if not up.exists():
                return redirect(create_profile_url)
            else:
                # The user has created a profile
                return None
        return None
