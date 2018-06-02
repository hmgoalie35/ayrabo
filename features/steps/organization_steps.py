from behave import *

from organizations.tests import OrganizationFactory


@step('The following organization objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()

        kwargs = {
            'name': data.get('name')
        }

        obj_id = data.get('id')
        if obj_id:
            kwargs['id'] = obj_id

        OrganizationFactory(**kwargs)
