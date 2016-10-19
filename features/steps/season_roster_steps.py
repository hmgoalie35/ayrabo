from behave import *

from accounts.tests import UserFactory
from players.tests import HockeyPlayerFactory
from seasons.models import Season
from seasons.tests import HockeySeasonRosterFactory
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
        players = data.get('players', None)
        factory_kwargs = {'season': season, 'team': team}
        if players:
            players = players.split(',')
            player_objs = []
            for player_name in players:
                player_name = player_name.strip().split(' ')
                first_name = player_name[0]
                last_name = player_name[1]
                user = UserFactory(first_name=first_name, last_name=last_name)
                player_objs.append(HockeyPlayerFactory(user=user, sport=team.division.league.sport, team=team))
            factory_kwargs['players'] = [player.pk for player in player_objs]

        factory_cls(**factory_kwargs)
