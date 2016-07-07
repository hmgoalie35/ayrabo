from behave import *

from divisions.tests.factories.DivisionFactory import DivisionFactory
from leagues.tests.factories.LeagueFactory import LeagueFactory


@step('The following division exists "(?P<division_name>[^"]*)"')
def step_impl(context, division_name):
    DivisionFactory(name=division_name)


@step('The following division exists "(?P<division_name>.*)" in league "(?P<league_name>.*)"')
def step_impl(context, division_name, league_name):
    league = LeagueFactory(full_name=league_name)
    DivisionFactory(name=division_name, league=league)
