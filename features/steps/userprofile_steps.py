from behave import *
from django.db.models import Q

from userprofiles.models import UserProfile


@step('"(?P<username_or_email>.*)" has a userprofile with roles? "(?P<roles>.*)"')
def step_impl(context, username_or_email, roles):
    split_roles = roles.split(',')
    if ',' not in roles and len(split_roles) > 1:
        raise ValueError('Roles must be separated by commas')
    roles_list = [role.strip() for role in split_roles]
    userprofile = UserProfile.objects.get(Q(user__email=username_or_email) | Q(user__username=username_or_email))
    userprofile.is_complete = False
    userprofile.set_roles(roles_list)
    userprofile.save()
