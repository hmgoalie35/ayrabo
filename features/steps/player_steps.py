from behave import *
from django.contrib.auth.models import User
from django.db.models import Q

from accounts.tests import UserFactory
from players.tests import HockeyPlayerFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory


@step('The following player objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()

        username_or_email = data.get('username_or_email')
        user = User.objects.filter(Q(email=username_or_email) | Q(username=username_or_email))
        if user.exists():
            user = user.first()
        else:
            user = UserFactory(username=username_or_email, email=username_or_email)

        sport_name = data.get('sport', None)
        team_name = data.get('team', None)
        jersey_number = data.get('jersey_number', None)
        team = TeamFactory(name=team_name)

        sport = SportFactory(name=sport_name)

        kwargs = {
            'user': user,
            'sport': sport,
            'team': team
        }

        if jersey_number is not None:
            kwargs['jersey_number'] = jersey_number

        HockeyPlayerFactory(**kwargs)
