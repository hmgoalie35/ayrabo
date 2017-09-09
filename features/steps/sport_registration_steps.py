from behave import *

from escoresheet.utils.testing import get_user
from sports.models import Sport, SportRegistration
from sports.tests import SportRegistrationFactory


@step(
        '"(?P<username_or_email>.*)" is (?P<is_complete>completely )?registered for "(?P<sport_name>.*)" with roles? "(?P<roles>.*)"')  # noqa
def step_impl(context, username_or_email, is_complete, sport_name, roles):
    split_roles = roles.split(',')
    if ',' not in roles and len(split_roles) > 1:
        raise ValueError('Roles must be separated by commas')
    roles_list = [role.strip() for role in split_roles]
    user = get_user(username_or_email)
    sport = Sport.objects.filter(name=sport_name)
    complete = is_complete is not None
    if sport.exists():
        sr = SportRegistrationFactory(user=user, sport=sport.first(), is_complete=complete)
    else:
        sr = SportRegistrationFactory(user=user, sport__name=sport_name, is_complete=complete)
    sr.set_roles(roles_list)
    context.url_kwargs.update({sr.sport.name: sr.pk})


@step('The sport registration for "(?P<username_or_email>.*)" and "(?P<sport_name>.*)" is complete')
def step_impl(context, username_or_email, sport_name):
    user = get_user(username_or_email)
    sr = SportRegistration.objects.get(user=user, sport__name=sport_name)
    sr.is_complete = True
    sr.save()


@step('The following sport registrations? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        username_or_email = data.get('username_or_email', None)
        sport_name = data.get('sport', None)
        roles = data.get('roles', [])
        complete = data.get('complete', 'false').lower() == 'true'
        obj_id = data.get('id', None)

        if username_or_email is None or sport_name is None or roles is None:
            raise Exception('You must specify user, sport and roles')

        user = get_user(username_or_email)
        sport = Sport.objects.filter(name=sport_name)
        kwargs = {'user': user, 'is_complete': complete}
        if sport.exists():
            kwargs['sport'] = sport.first()
        else:
            kwargs['sport__name'] = sport_name

        if obj_id is not None:
            kwargs['id'] = obj_id

        sr = SportRegistrationFactory(**kwargs)
        sr.set_roles([role.strip() for role in roles.split(',')])
        context.url_kwargs.update({sr.sport.name: sr.pk})


@given('I add the "(?P<roles>[^"]*)" roles? to "(?P<username_or_email>[^"]*)" for "(?P<sport_name>[^"]*)"')
def step_impl(context, roles, username_or_email, sport_name):
    user = get_user(username_or_email)
    sport_registration = SportRegistration.objects.get(user=user, sport__name=sport_name)
    sport_registration.set_roles([role.strip() for role in roles.split(',')], True)
