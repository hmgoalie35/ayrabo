from behave import *

from escoresheet.utils.testing import get_user
from leagues.models import League
from leagues.tests import LeagueFactory
from referees.tests import RefereeFactory


@step('The following referee objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        username_or_email = data.get('username_or_email')
        user = get_user(username_or_email)
        league = data.get('league', None)
        obj_id = data.get('id', None)

        leagues = League.objects.filter(full_name=league)

        if leagues.exists():
            league = leagues.first()
        else:
            league = LeagueFactory(full_name=league)

        kwargs = {'user': user, 'league': league}
        if obj_id is not None:
            kwargs['id'] = obj_id

        RefereeFactory(**kwargs)
