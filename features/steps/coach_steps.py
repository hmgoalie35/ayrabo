from behave import *
from django.db.models import Q

from coaches.models import Coach


@step('A coach object should exist for "(?P<username_or_email>.*)" for division "(?P<division>.*)" and team "(?P<team>.*)"')
def step_impl(context, username_or_email, division, team):
    coach = Coach.objects.get(Q(user__email=username_or_email) | Q(user__username=username_or_email))
    context.test.assertEqual(str(coach.team), '{division} - {team}'.format(division=division, team=team))
