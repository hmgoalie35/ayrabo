from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from userprofiles.models import UserProfile


class UserProfileExistsMiddleware(object):
    def process_request(self, request):
        """
        This middleware forces users to fill out a userprofile if they do not already have one. Any request to a url not
        in the whitelisted urls list will result in a redirect to the create_userprofile page. Users are still able
        to logout if they don't have a userprofile
        """
        create_profile_url = reverse('create_userprofile')
        finish_profile_url = reverse('finish_userprofile')
        whitelisted_urls = [reverse('account_logout'), create_profile_url, finish_profile_url]
        # Do not apply this middleware to anonymous users, or for any request to a whitelisted url
        if request.user.is_authenticated() and request.path not in whitelisted_urls:
            # Do not apply this middleware if the user already has a userprofile
            up = UserProfile.objects.filter(user=request.user)
            if not up.exists():
                return redirect(create_profile_url)
            elif not up.first().is_complete:
                return redirect(finish_profile_url)
        return None
