from behave import *

from escoresheet.utils import get_user
from managers.tests import ManagerFactory
from teams.models import Team
from teams.tests import TeamFactory


@step('The following manager objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()

        username_or_email = data.get('username_or_email')
        user = get_user(username_or_email)
        team = data.get('team', None)
        teams = Team.objects.filter(name=team)

        if teams.exists():
            team = teams.first()
        else:
            team = TeamFactory(name=team)
        ManagerFactory(user=user, team=team)
