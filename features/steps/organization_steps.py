from behave import *

from organizations.tests import OrganizationFactory
from sports.models import Sport


@step('The following organization objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()

        kwargs = {
            'name': data.get('name')
        }

        sports = Sport.objects.filter(name=data.get('sport'))
        if sports.exists():
            kwargs['sport'] = sports.first()

        obj_id = data.get('id')
        if obj_id:
            kwargs['id'] = obj_id

        OrganizationFactory(**kwargs)
