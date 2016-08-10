from behave import *
from django.contrib.auth.models import User
from django.db.models import Q

from coaches.models import Coach
from coaches.tests import CoachFactory
from teams.models import Team
from teams.tests.factories.TeamFactory import TeamFactory


@step(
        'A coach object should exist for "(?P<username_or_email>.*)" for division "(?P<division>.*)" and team "(?P<team>.*)"')
def step_impl(context, username_or_email, division, team):
    coach = Coach.objects.get(Q(user__email=username_or_email) | Q(user__username=username_or_email))
    context.test.assertEqual(str(coach.team), '{division} - {team}'.format(division=division, team=team))


@step('The following coach objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()

        username_or_email = data.get('username_or_email')
        user = User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))
        team = data.get('team', None)
        position = data.get('position', None)

        teams = Team.objects.filter(name=team)
        if teams.exists():
            team = teams.first()
        else:
            team = TeamFactory(name=team)
        CoachFactory(user=user, team=team, position=position)
