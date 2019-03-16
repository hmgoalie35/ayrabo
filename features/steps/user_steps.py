from behave import *

from ayrabo.utils.testing import clean_kwargs, get_user, handle_date, to_bool
from features.steps.generic_steps import get_first_obj_for_model
from userprofiles.tests import UserProfileFactory
from users.tests import PermissionFactory, UserFactory


@step('"(?P<username_or_email>[^"]+)" has the "(?P<name>[a-z]+)" permission for "(?P<model>[^"]+)" with kwargs "(?P<kwargs>.*)"')  # noqa
def step_impl(context, username_or_email, name, model, kwargs):
    user = get_user(username_or_email)
    content_object = get_first_obj_for_model(model, kwargs)

    PermissionFactory(name=name, user=user, content_object=content_object)


@step(r"The following users? exist")
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        email = data.get('email')
        create_userprofile = to_bool(data.get('create_userprofile', True))
        kwargs = {
            'id': data.get('id'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'email': email,
            'username': data.get('username', email),
            'password': data.get('password')
        }
        kwargs = clean_kwargs(kwargs)
        # This needs to be after we clean the kwargs.
        if not create_userprofile:
            kwargs.update({'userprofile': None})
        UserFactory(**kwargs)


@step(r"The following userprofiles? exist")
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        username_or_email = data.get('username_or_email')
        user = get_user(username_or_email)
        gender = data.get('gender')
        birthday = data.get('birthday')
        height = data.get('height')
        weight = data.get('weight')
        language = data.get('language')
        timezone = data.get('timezone')
        kwargs = {
            'user': user,
            'gender': gender,
            'birthday': handle_date(birthday),
            'height': height,
            'weight': weight,
            'language': language,
            'timezone': timezone
        }
        kwargs = clean_kwargs(kwargs)
        UserProfileFactory(**kwargs)
