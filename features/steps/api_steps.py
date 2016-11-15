from behave import *

from api.tests import TokenFactory
from escoresheet.utils import get_user


@step('"(?P<username_or_email>.*)" has "(?P<token>.*)" as an api token')
def step_impl(context, username_or_email, token):
    user = get_user(username_or_email)
    TokenFactory(user=user, key=token)
