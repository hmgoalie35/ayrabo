from behave import *

from sports.tests import SportFactory


@step('The sport "(?P<sport_name>[^"]*)" already exists')
def step_impl(context, sport_name):
    SportFactory(name=sport_name)


@step('The following sport exists "(?P<sport_name>.*)"')
def step_impl(context, sport_name):
    SportFactory(name=sport_name)


@step('The following sport objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        SportFactory(**data)
