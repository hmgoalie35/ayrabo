from behave import *

from ayrabo.utils.testing import clean_kwargs, get_user
from features.steps.generic_steps import get_first_obj_for_model
from users.tests import PermissionFactory, UserFactory


@step('"(?P<username_or_email>[^"]+)" has the "(?P<name>[a-z]+)" permission for "(?P<model>[^"]+)" with kwargs "(?P<kwargs>.*)"')  # noqa
def step_impl(context, username_or_email, name, model, kwargs):
    user = get_user(username_or_email)
    content_object = get_first_obj_for_model(model, kwargs)

    PermissionFactory(name=name, user=user, content_object=content_object)


@step("The following users? exist")
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        email = data.get('email')
        kwargs = {
            'id': data.get('id'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'email': email,
            'username': data.get('username', email)
        }
        kwargs = clean_kwargs(kwargs)
        UserFactory(**kwargs)
