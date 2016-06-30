from behave import *
from divisions.tests.factories.DivisionFactory import DivisionFactory


@step('The following division exists "(?P<division_name>.*)"')
def step_impl(context, division_name):
    DivisionFactory.create(name=division_name)
