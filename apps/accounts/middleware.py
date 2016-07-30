from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from userprofiles.models import UserProfile, RolesMask


class AccountRegistrationCompleteMiddleware(object):
    """
    This middleware makes sure a user has created a userprofile, chosen the roles for every sport they
    registered for and that the corresponding Coach, Referee, etc. objects have been created.
    """
    def process_request(self, request):
        create_profile_url = reverse('profile:create')
        select_roles_url = reverse('profile:select_roles')
        finish_profile_url = reverse('profile:finish')
        whitelisted_urls = [reverse('account_logout'), create_profile_url, select_roles_url, finish_profile_url]

        # debug_toolbar wasn't working properly because of my custom middleware so let all debug_toolbar
        # requests through
        if '__debug__' in request.path:
            return None

        # Do not apply this middleware to anonymous users, or for any request to a whitelisted url. An infinite redirect
        # loop would occur if create_profile_url, select_roles_url and finish_profile_url weren't whitelisted
        if request.user.is_authenticated() and request.path not in whitelisted_urls:
            up = UserProfile.objects.filter(user=request.user)
            roles_not_set = RolesMask.objects.filter(user=request.user, are_roles_set=False)
            objects_not_created = RolesMask.objects.filter(user=request.user, are_role_objects_created=False)
            # A user's account is deemed "complete" when a userprofile exists, they have chosen their desired roles
            # for all sports they chose, and the appropriate role objects (Coach, Referee, etc.) have been created
            if not up.exists():
                return redirect(create_profile_url)
            elif roles_not_set.exists():
                return redirect(select_roles_url)
            elif objects_not_created.exists():
                return redirect(finish_profile_url)
            else:
                # The user's account is "complete"
                return None
        return None
