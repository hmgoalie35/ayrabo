from behave import *

from leagues.tests import LeagueFactory


@step('The following league exists "(?P<league_name>[^"]*)"')
def step_impl(context, league_name):
    LeagueFactory(name=league_name)


@step('The following league exists "(?P<league_name>.*)" in sport "(?P<sport>.*)"')
def step_impl(context, league_name, sport):
    LeagueFactory(name=league_name, sport__name=sport)


@step('The following league objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()

        if 'sport' in data:
            data['sport__name'] = data.pop('sport')

        LeagueFactory(**data)
