from behave import *
from django.contrib.auth.models import User
from django.db.models import Q

from sports.models import Sport, SportRegistration
from sports.tests.factories.SportRegistrationFactory import SportRegistrationFactory


@step('"(?P<username_or_email>.*)" is (?P<is_complete>completely )?registered for "(?P<sport_name>.*)" with roles? "(?P<roles>.*)"')
def step_impl(context, username_or_email, is_complete, sport_name, roles):
    split_roles = roles.split(',')
    if ',' not in roles and len(split_roles) > 1:
        raise ValueError('Roles must be separated by commas')
    roles_list = [role.strip() for role in split_roles]
    user = User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))
    sport = Sport.objects.filter(name=sport_name)
    complete = is_complete is not None
    if sport.exists():
        sr = SportRegistrationFactory(user=user, sport=sport.first(), is_complete=complete)
    else:
        sr = SportRegistrationFactory(user=user, sport__name=sport_name, is_complete=complete)
    sr.set_roles(roles_list)


@step('The sport registration for "(?P<username_or_email>.*)" and "(?P<sport_name>.*)" is complete')
def step_impl(context, username_or_email, sport_name):
    user = User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))
    sr = SportRegistration.objects.get(user=user, sport__name=sport_name)
    sr.is_complete = True
    sr.save()
