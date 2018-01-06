import datetime

import pytz
from behave import *

from common.models import GenericChoice
from games.tests import HockeyGameFactory
from locations.models import Location
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
        timezone = data.get('timezone')
        tz = pytz.timezone(timezone)

        kwargs = {
            'home_team': get_object(Team, name=data.get('home_team')),
            'away_team': get_object(Team, name=data.get('away_team')),
            'type': get_object(GenericChoice, short_value=data.get('type')),
            'point_value': get_object(GenericChoice, short_value=data.get('point_value')),
            'location': get_object(Location, name=data.get('location')),
            'season': get_object(Season, id=data.get('season')),
            'start': parse_datetime(data.get('start'), tz),
            'end': parse_datetime(data.get('end'), tz),
            'timezone': timezone
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        HockeyGameFactory(**kwargs)
