import datetime

import pytz
from behave import *
from django.utils import timezone

from common.models import GenericChoice
from escoresheet.utils.testing import string_to_kwargs_dict
from games.models import HockeyGame
from games.tests import HockeyGameFactory
from locations.models import Location
from players.models import HockeyPlayer
from seasons.models import Season
from teams.models import Team


def get_object(cls, **kwargs):
    try:
        return cls.objects.get(**kwargs)
    except cls.DoesNotExist:
        return None


def parse_datetime(datetime_str, tz, dt_format='%m/%d/%Y %I:%M %p'):
    return tz.localize(datetime.datetime.strptime(datetime_str, dt_format))


@step('The following game objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        tz_string = data.get('timezone')
        tz = pytz.timezone(tz_string)
        obj_id = data.get('id', None)
        if obj_id == '':
            obj_id = None

        home_team = get_object(Team, name=data.get('home_team'))
        start = data.get('start', None)
        if start == 'today':
            start = timezone.now()
        end = data.get('end', None)
        if end == 'today':
            end = start + datetime.timedelta(hours=3)

        kwargs = {
            'id': obj_id,
            'home_team': home_team,
            'team': home_team,
            'away_team': get_object(Team, name=data.get('away_team')),
            'type': get_object(GenericChoice, short_value=data.get('type')),
            'point_value': get_object(GenericChoice, short_value=data.get('point_value')),
            'location': get_object(Location, name=data.get('location')),
            'season': get_object(Season, id=data.get('season')),
            'start': parse_datetime(start, tz) if isinstance(start, str) else start,
            'end': parse_datetime(end, tz) if isinstance(end, str) else end,
            'timezone': tz_string,
            'status': data.get('status', None)
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        HockeyGameFactory(**kwargs)


@step('"(?P<player_ids>[^"]*)" is added to "(?P<roster>home_players|away_players)" for the game with kwargs "(?P<kwarg_data>[^"]*)"')  # noqa
def step_impl(context, player_ids, roster, kwarg_data):
    ids = [int(p.strip()) for p in player_ids.split(',')]
    players = [HockeyPlayer.objects.get(id=p_id) for p_id in ids]
    kwargs = string_to_kwargs_dict(kwarg_data)
    game = get_object(HockeyGame, **kwargs)
    getattr(game, roster).add(*players)
