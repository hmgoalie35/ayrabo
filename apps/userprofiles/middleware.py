from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from userprofiles.models import UserProfile, RolesMask


class UserProfileExistsMiddleware(object):
    def process_request(self, request):
        """
        This middleware forces users to fill out a userprofile if they do not already have one. Any request to a url not
        in the whitelisted urls list will result in a redirect to the profile:create page. Users are still able
        to logout if they don't have a userprofile
        """
        create_profile_url = reverse('profile:create')
        finish_profile_url = reverse('profile:finish')
        select_roles_url = reverse('profile:select_roles')
        whitelisted_urls = [reverse('account_logout'), create_profile_url, finish_profile_url, select_roles_url]
        # debug_toolbar wasn't working properly because of my custom middleware
        # so let all debug_toolbar requests through
        if '__debug__' in request.path:
            return None

        # Do not apply this middleware to anonymous users, or for any request to a whitelisted url
        if request.user.is_authenticated() and request.path not in whitelisted_urls:
            # Do not apply this middleware if the user already has a userprofile
            up = UserProfile.objects.filter(user=request.user)
            incomplete_roles_masks = RolesMask.objects.filter(user=request.user, is_complete=False)
            if not up.exists():
                return redirect(create_profile_url)
            elif incomplete_roles_masks.exists():
                return redirect(select_roles_url)
            elif not up.first().is_complete:
                return redirect(finish_profile_url)
        return None
