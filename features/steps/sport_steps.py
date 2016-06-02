from behave import *
from sports.tests.factories.SportFactory import SportFactory


@step('The sport "(?P<sport_name>[^"]*)" already exists')
def step_impl(context, sport_name):
    SportFactory.create(name=sport_name)
