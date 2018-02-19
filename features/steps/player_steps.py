from behave import *

from users.tests import UserFactory
from ayrabo.utils.testing import get_user
from players.tests import HockeyPlayerFactory
from sports.models import Sport
from sports.tests import SportFactory
from teams.models import Team
from teams.tests import TeamFactory
from users.models import User


@step('The following player objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()

        username_or_email = data.get('username_or_email')
        try:
            user = get_user(username_or_email)
        except User.DoesNotExist:
            user = UserFactory(username=username_or_email, email=username_or_email)

        obj_id = data.get('id', None)
        sport = data.get('sport', None)
        team = data.get('team', None)
        jersey_number = data.get('jersey_number', None)

        teams = Team.objects.filter(name=team)
        if teams.exists():
            team = teams.first()
        else:
            team = TeamFactory(name=team)

        sports = Sport.objects.filter(name=sport)
        if sports.exists():
            sport_obj = sports.first()
        else:
            sport_obj = SportFactory(name=sport)

        kwargs = {
            'user': user,
            'sport': sport_obj,
            'team': team
        }

        if jersey_number is not None:
            kwargs['jersey_number'] = jersey_number
        if obj_id is not None:
            kwargs['id'] = obj_id

        HockeyPlayerFactory(**kwargs)
