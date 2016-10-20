from behave import *

from escoresheet.utils import get_user
from leagues.tests import LeagueFactory
from referees.tests import RefereeFactory


@step('The following referee objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        username_or_email = data.get('username_or_email')
        user = get_user(username_or_email)
        league = data.get('league', None)

        league = LeagueFactory(full_name=league)
        RefereeFactory(user=user, league=league)
