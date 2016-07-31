from behave import *

from leagues.tests.factories.LeagueFactory import LeagueFactory


@step('The following league exists "(?P<league_name>[^"]*)"')
def step_impl(context, league_name):
    LeagueFactory(full_name=league_name)


@step('The following league exists "(?P<league_name>.*)" in sport "(?P<sport>.*)"')
def step_impl(context, league_name, sport):
    LeagueFactory(full_name=league_name, sport__name=sport)
