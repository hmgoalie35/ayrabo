from behave import *

from locations.tests import LocationFactory


@step('The following location objects? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()
        obj_id = data.pop('id', None)
        if obj_id:
            data['id'] = obj_id
        LocationFactory(**data)
