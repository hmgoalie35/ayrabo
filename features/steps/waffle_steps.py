from behave import *

from ayrabo.utils.testing import clean_kwargs, to_bool
from common.tests import WaffleSwitchFactory


@step('The following waffle switch[es]? exists?')
def step_impl(context):
    for row in context.table:
        data = row.as_dict()

        kwargs = {
            'name': data.get('name'),
            'active': to_bool(data.get('active')),
            'note': data.get('note')
        }

        kwargs = clean_kwargs(kwargs)

        WaffleSwitchFactory(**kwargs)
