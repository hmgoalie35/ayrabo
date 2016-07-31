from behave import *
from django.contrib.auth.models import User
from django.db.models import Q

from sports.models import Sport
from userprofiles.models import RolesMask
from userprofiles.tests.factories.RolesMaskFactory import RolesMaskFactory


@step('A rolesmask exists for "(?P<username_or_email>.*)" for "(?P<sport_name>.*)" with roles? "(?P<roles>.*)"')
def step_impl(context, username_or_email, sport_name, roles):
    split_roles = roles.split(',')
    if ',' not in roles and len(split_roles) > 1:
        raise ValueError('Roles must be separated by commas')
    roles_list = [role.strip() for role in split_roles]
    user = User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))
    sport = Sport.objects.filter(name=sport_name)
    if sport.exists():
        rm = RolesMaskFactory(user=user, sport=sport.first(), are_roles_set=True, are_role_objects_created=False)
    else:
        rm = RolesMaskFactory(user=user, sport__name=sport_name, are_roles_set=True, are_role_objects_created=False)
    rm.set_roles(roles_list)
    rm.save()


@step('A rolesmask exists for "(?P<username_or_email>.*)" for "(?P<sport_name>.*)"')
def step_impl(context, username_or_email, sport_name):
    user = User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))
    RolesMaskFactory(user=user, sport__name=sport_name, are_roles_set=False, are_role_objects_created=False)


@given('The rolesmask for "(?P<username_or_email>.*)" and "(?P<sport_name>.*)" is complete')
def step_impl(context, username_or_email, sport_name):
    user = User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))
    rm = RolesMask.objects.get(user=user, sport__name=sport_name)
    rm.are_role_objects_created = True
    rm.are_roles_set = True
    rm.save()
