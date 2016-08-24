from behave import *
from django.contrib.auth.models import User
from django.db.models import Q

from api.tests import TokenFactory


@step('"(?P<username_or_email>.*)" has "(?P<token>.*)" as an api token')
def step_impl(context, username_or_email, token):
    user = User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))
    TokenFactory(user=user, key=token)
