from behave import *

from ayrabo.utils.testing import get_user
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory


def clean_roles(roles):
    return [role.strip().lower() for role in roles.split(',')]


@step('"(?P<username_or_email>.*)" is (?P<is_complete>completely )?registered for "(?P<sport_name>.*)" with roles? "(?P<roles>.*)"')  # noqa
def step_impl(context, username_or_email, is_complete, sport_name, roles):
    user = get_user(username_or_email)
    sport = SportFactory(name=sport_name)
    complete = is_complete is not None
    for role in clean_roles(roles):
        SportRegistrationFactory(user=user, sport=sport, is_complete=complete, role=role)


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

        username_or_email = data.get('username_or_email')
        sport_name = data.get('sport')
        roles = data.get('roles')
        complete = data.get('complete', 'false').lower() == 'true'
        obj_id = data.get('id')

        user = get_user(username_or_email)
        sport = SportFactory(name=sport_name)

        kwargs = {'user': user, 'is_complete': complete, 'sport': sport}
        if obj_id is not None:
            kwargs['id'] = obj_id

        for role in clean_roles(roles):
            SportRegistrationFactory(**kwargs, role=role)
