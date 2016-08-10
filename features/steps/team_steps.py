from behave import *

from divisions.tests.factories.DivisionFactory import DivisionFactory
from leagues.tests.factories.LeagueFactory import LeagueFactory
from sports.tests.factories.SportFactory import SportFactory
from teams.tests.factories.TeamFactory import TeamFactory


@step('The following team exists "(?P<team_name>[^"]*)" in division "(?P<division>[^"]*)"')
def step_impl(context, team_name, division):
    div = DivisionFactory.create(name=division)
    TeamFactory.create(name=team_name, division=div)


@step(
        'The following team exists "(?P<team_name>.*)" in division "(?P<division_name>.*)" in league "(?P<league_name>.*)" in sport "(?P<sport_name>.*)"')
def step_impl(context, team_name, division_name, league_name, sport_name):
    sport = SportFactory(name=sport_name)
    league = LeagueFactory(full_name=league_name, sport=sport)
    division = DivisionFactory(name=division_name, league=league)
    TeamFactory(name=team_name, division=division)
