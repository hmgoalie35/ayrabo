from behave import *
from django.contrib.auth.models import User
from django.db.models import Q

from accounts.tests import UserFactory
from players.tests import HockeyPlayerFactory
from sports.models import Sport
from sports.tests import SportFactory
from teams.models import Team
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

        if jersey_number is None:
            HockeyPlayerFactory(user=user, sport=sport_obj, team=team)
        else:
            HockeyPlayerFactory(user=user, sport=sport_obj, team=team, jersey_number=jersey_number)
