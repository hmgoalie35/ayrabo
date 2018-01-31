from behave import *

from escoresheet.utils.testing import get_user
from scorekeepers.tests import ScorekeeperFactory
from sports.models import Sport
from sports.tests import SportFactory


@step('The following scorekeeper objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        username_or_email = data.get('username_or_email')
        user = get_user(username_or_email)
        sport = data.get('sport', None)
        obj_id = data.get('id', None)

        sports = Sport.objects.filter(name=sport)

        if sports.exists():
            sport = sports.first()
        else:
            sport = SportFactory(name=sport)

        kwargs = {'user': user, 'sport': sport}
        if obj_id is not None:
            kwargs['id'] = obj_id

        ScorekeeperFactory(**kwargs)
