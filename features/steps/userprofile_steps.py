from behave import *
from userprofiles.models import UserProfile
from django.db.models import Q


@step('"(?P<username_or_email>.*)" has a userprofile with roles "(?P<roles>.*)"')
def step_impl(context, username_or_email, roles):
    if ',' not in roles:
        raise ValueError('Roles must be separated by commas')
    roles_list = [role.strip() for role in roles.split(',')]
    userprofile = UserProfile.objects.get(Q(user__email=username_or_email) | Q(user__username=username_or_email))
    userprofile.is_complete = False
    userprofile.set_roles(roles_list)
    userprofile.save()
