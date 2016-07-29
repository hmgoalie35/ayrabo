from behave import *
from django.contrib.auth.models import User
from userprofiles.models import RolesMask
from django.db.models import Q

from userprofiles.tests.factories.RolesMaskFactory import RolesMaskFactory


@step('A rolesmask exists for "(?P<username_or_email>.*)" for "(?P<sport_name>.*)"')
def step_impl(context, username_or_email, sport_name):
    user = User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))
    RolesMaskFactory(user=user, sport__name=sport_name, is_complete=False)


@given('The rolesmask for "(?P<username_or_email>.*)" and "(?P<sport_name>.*)" is complete')
def step_impl(context, username_or_email, sport_name):
    user = User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))
    rm = RolesMask.objects.get(user=user, sport__name=sport_name)
    rm.is_complete = True
    rm.save()
