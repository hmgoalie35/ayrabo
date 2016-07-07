from behave import *

from leagues.tests.factories.LeagueFactory import LeagueFactory


@step('The following league exists "(?P<league_name>.*)"')
def step_impl(context, league_name):
    LeagueFactory(full_name=league_name)
