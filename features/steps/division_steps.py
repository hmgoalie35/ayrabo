from behave import *

from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory


@step('The following division exists "(?P<division_name>[^"]*)"')
def step_impl(context, division_name):
    DivisionFactory(name=division_name)


@step('The following division exists "(?P<division_name>.*)" in league "(?P<league_name>.*)"')
def step_impl(context, division_name, league_name):
    league = LeagueFactory(name=league_name)
    DivisionFactory(name=division_name, league=league)


@step('The following division objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()

        if 'league' in data:
            data['league__name'] = data.pop('league')

        DivisionFactory(**data)
