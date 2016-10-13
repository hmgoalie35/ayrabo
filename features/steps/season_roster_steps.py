from behave import *

from seasons.tests import HockeySeasonRosterFactory
from seasons.models import Season
from teams.models import Team

SPORT_SEASON_ROSTER_FACTORY_MAPPINGS = {
    'Ice Hockey': HockeySeasonRosterFactory
}


@step('The following season rosters? for "(?P<sport_name>[^"]*)" exists?')
def step_impl(context, sport_name):
    for row in context.table:
        data = row.as_dict()
        factory_cls = SPORT_SEASON_ROSTER_FACTORY_MAPPINGS[sport_name]
        season_start_date = data.get('season_start_date')
        season_end_date = data.get('season_end_date')
        team = Team.objects.get(name=data.get('team'))
        season = Season.objects.get(start_date=season_start_date, end_date=season_end_date)
        # Add in players if necessary
        factory_cls(season=season, team=team)
