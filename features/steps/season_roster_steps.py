import datetime

from behave import *

from ayrabo.utils.testing import get_user, clean_kwargs
from players.tests import HockeyPlayerFactory
from seasons.models import Season, HockeySeasonRoster
from seasons.tests import HockeySeasonRosterFactory
from teams.models import Team
from users.tests import UserFactory

SPORT_SEASON_ROSTER_FACTORY_MAPPINGS = {
    'Ice Hockey': HockeySeasonRosterFactory
}

SPORT_PLAYER_FACTORY_MAPPINGS = {
    'Ice Hockey': HockeyPlayerFactory
}

SPORT_SEASON_ROSTER_MAPPINGS = {
    'Ice Hockey': HockeySeasonRoster
}


@step('The following season rosters? for "(?P<sport_name>[^"]*)" exists?')
def step_impl(context, sport_name):
    for row in context.table:
        data = row.as_dict()
        factory_cls = SPORT_SEASON_ROSTER_FACTORY_MAPPINGS[sport_name]
        today = datetime.date.today()

        season_id = data.get('season_id')
        season_start_date = data.get('season_start_date', today)
        season_end_date = data.get('season_end_date', today + datetime.timedelta(days=365))
        season_kwargs = {}
        if season_id:
            season_kwargs['id'] = season_id
        else:
            season_kwargs['start_date'] = season_start_date
            season_kwargs['end_date'] = season_end_date
        season = Season.objects.get(**season_kwargs)

        obj_id = data.get('id')
        team = Team.objects.get(name=data.get('team'))
        players = data.get('players', None)
        created_by = data.get('created_by', None)
        created_by = get_user(created_by) if created_by else None
        factory_kwargs = {
            'season': season,
            'team': team,
            'default': data.get('default', False),
            'name': data.get('name')
        }
        if created_by:
            factory_kwargs.update({'created_by': created_by})
        if obj_id:
            factory_kwargs['id'] = obj_id

        if players:
            players = players.split(',')
            player_objs = []
            sport = team.division.league.sport
            for player_name in players:
                player_name = player_name.strip().split(' ')
                first_name = player_name[0]
                last_name = player_name[1]
                user = UserFactory(first_name=first_name, last_name=last_name)
                player_objs.append(HockeyPlayerFactory(user=user, sport=sport, team=team))
            factory_kwargs['players'] = [player.pk for player in player_objs]

        factory_cls(**factory_kwargs)


@step('The following "(?P<sport_name>[^"]+)" players? have been added to season roster "(?P<season_roster_id>[^"]+)"')
def step_impl(context, sport_name, season_roster_id):
    player_factory_cls = SPORT_PLAYER_FACTORY_MAPPINGS.get(sport_name)
    season_roster_cls = SPORT_SEASON_ROSTER_MAPPINGS.get(sport_name)
    season_roster = season_roster_cls.objects.get(id=season_roster_id)
    players = []
    for row in context.table:
        data = row.as_dict()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        jersey_number = data.get('jersey_number')
        position = data.get('position')
        team = Team.objects.get(id=data.get('team_id'))
        user_kwargs = {
            'first_name': first_name,
            'last_name': last_name
        }
        user = UserFactory(**clean_kwargs(user_kwargs))
        factory_kwargs = {
            'user': user,
            'jersey_number': jersey_number,
            'position': position,
            'team': team
        }
        player = player_factory_cls(**clean_kwargs(factory_kwargs))
        players.append(player)

    season_roster.players.add(*players)
