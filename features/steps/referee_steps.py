from behave import *
from django.contrib.auth.models import User
from django.db.models import Q

from referees.tests.factories.RefereeFactory import RefereeFactory
from leagues.models import League
from leagues.tests.factories.LeagueFactory import LeagueFactory


@step('The following referee objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        username_or_email = data.get('username_or_email')
        user = User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))
        league = data.get('league', None)

        leagues = League.objects.filter(full_name=league)
        if leagues.exists():
            league = leagues.first()
        else:
            league = LeagueFactory(full_name=league)
        RefereeFactory(user=user, league=league)
