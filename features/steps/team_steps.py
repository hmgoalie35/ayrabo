from behave import *

from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory


@step('The following team exists "(?P<team_name>[^"]*)" in division "(?P<division>[^"]*)"')
def step_impl(context, team_name, division):
    div = DivisionFactory(name=division)
    TeamFactory(name=team_name, division=div)


@step(
        'The following team exists "(?P<team_name>.*)" in division "(?P<division_name>.*)" in league "(?P<league_name>.*)" in sport "(?P<sport_name>.*)"')  # noqa
def step_impl(context, team_name, division_name, league_name, sport_name):
    sport = SportFactory(name=sport_name)
    league = LeagueFactory(full_name=league_name, sport=sport)
    division = DivisionFactory(name=division_name, league=league)
    TeamFactory(name=team_name, division=division)


@step('The following team objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        sport = league = division = None

        if 'sport' in data:
            sport = SportFactory(name=data.pop('sport'))
        if 'league' in data and sport:
            league = LeagueFactory(full_name=data.pop('league'), sport=sport)
        if 'division' in data and league:
            division = DivisionFactory(name=data.pop('division'), league=league)
        print(data)
        data['division'] = division
        TeamFactory(**data)
