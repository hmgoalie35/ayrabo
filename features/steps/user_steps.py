from behave import *
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from accounts.tests import EmailAddressFactory
from ayrabo.utils.testing import get_user, handle_date, to_bool
from userprofiles.tests import UserProfileFactory
from users.tests import PermissionFactory, UserFactory


@step(r"The following users exist")
def step_impl(context):
    for row in context.table:
        data = row.as_dict()

        obj_id = data.pop('id', None)
        username = data.get('username')
        email = data.get('email')
        account_type = data.pop('account_type', 'confirmed')
        create_userprofile = to_bool(data.pop('create_userprofile', True))

        data.update({
            'username': username or email,
            'is_active': to_bool(data.pop('is_active', True)),
        })
        if not create_userprofile:
            data.update({'userprofile': None})
        if obj_id:
            data.update({'id': obj_id})

        # NOTE: user factory creates a userprofile for us, unless `userprofile: None` is in the data dict
        user = UserFactory(**data)

        assert email, 'Email is required for this step.'
        email_verified = account_type == 'confirmed'
        email_address = EmailAddressFactory(user=user, email=email, verified=email_verified, primary=False)
        if account_type == 'unconfirmed':
            email_address.send_confirmation()


@step(r"The following userprofiles exist")
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        username_or_email = data.pop('username_or_email')
        data.update({
            'user': get_user(username_or_email),
            'birthday': handle_date(data.pop('birthday', None)),
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
