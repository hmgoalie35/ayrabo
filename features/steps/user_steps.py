from behave import *
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from ayrabo.utils.testing import get_user, handle_date, to_bool
from userprofiles.tests import UserProfileFactory
from users.tests import PermissionFactory, UserFactory


@step(r"The following users exist")
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        create_userprofile = to_bool(data.pop('create_userprofile', True))
        data.update({
            'username': data.get('username') or data.get('email'),
            'is_active': to_bool(data.pop('is_active', True)),
        })
        if not create_userprofile:
            data.update({'userprofile': None})
        UserFactory(**data)


@step(r"The following userprofiles exist")
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        username_or_email = data.get('username_or_email')
        data.update({
            'user': get_user(username_or_email),
            'birthday': handle_date(data.get('birthday')),
        })
        UserProfileFactory(**data)


@step(r"The following permissions exist")
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        user = get_user(data.get('username_or_email'))
        name = data.get('name')
        model = apps.get_model(data.get('model'))
        content_type = ContentType.objects.get_for_model(model)
        object_id = data.get('object_id')
        PermissionFactory(name=name, user=user, content_type=content_type, object_id=object_id)
