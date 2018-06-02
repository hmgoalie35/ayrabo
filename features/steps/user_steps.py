from behave import *

from ayrabo.utils.testing import get_user
from features.steps.generic_steps import get_first_obj_for_model
from users.tests import PermissionFactory


@step('"(?P<username_or_email>[^"]+)" has the "(?P<name>[a-z]+)" permission for "(?P<model>[^"]+)" with kwargs "(?P<kwargs>.*)"')  # noqa
def step_impl(context, username_or_email, name, model, kwargs):
    user = get_user(username_or_email)
    content_object = get_first_obj_for_model(model, kwargs)

    PermissionFactory(name=name, user=user, content_object=content_object)
