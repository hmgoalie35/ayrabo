from behave import *

from escoresheet.utils import get_user
from managers.tests import ManagerFactory
from teams.tests import TeamFactory


@step('The following manager objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()

        username_or_email = data.get('username_or_email')
        user = get_user(username_or_email)
        team_name = data.get('team', None)
        team = TeamFactory(name=team_name)
        ManagerFactory(user=user, team=team)
