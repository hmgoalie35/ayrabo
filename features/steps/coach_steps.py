from behave import *

from coaches.models import Coach
from coaches.tests import CoachFactory
from escoresheet.utils import get_user
from teams.tests import TeamFactory


@step(
        'A coach object should exist for "(?P<username_or_email>.*)" for division "(?P<division>.*)" and team "(?P<team>.*)"')
def step_impl(context, username_or_email, division, team):
    coach = Coach.objects.get(user=get_user(username_or_email))
    context.test.assertEqual(str(coach.team), '{division} - {team}'.format(division=division, team=team))


@step('The following coach objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()

        username_or_email = data.get('username_or_email')
        user = get_user(username_or_email)
        team_name = data.get('team', None)
        position = data.get('position', None)

        team = TeamFactory(name=team_name)
        CoachFactory(user=user, team=team, position=position)
