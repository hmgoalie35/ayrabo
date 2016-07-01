from behave import *

from divisions.tests.factories.DivisionFactory import DivisionFactory
from teams.tests.factories.TeamFactory import TeamFactory


@step('The following team exists "(?P<team_name>.*)" in division "(?P<division>.*)"')
def step_impl(context, team_name, division):
    div = DivisionFactory.create(name=division)
    TeamFactory.create(name=team_name, division=div)
