import json

from django import template

register = template.Library()


@register.filter
def booltojson(value):  # pragma: no cover
    """
    Converts python booleans to javascript booleans.
    See https://code.djangoproject.com/ticket/17419 for why we don't have a generic `tojson` filter.
    """
    if value in [True, False]:
        return json.dumps(value)
    return json.dumps(None)


@register.simple_tag
def pluralize_role(role):
    mappings = {
        'coach': 'Coaches',
        'manager': 'Managers',
        'player': 'Players',
        'referee': 'Referees',
        'scorekeeper': 'Scorekeepers',
        'organization': 'Organizations'
    }
    pluralized = mappings.get(role.lower())
    if pluralized is None:
        raise ValueError('Pluralization mapping does not exist for {}.'.format(role))
    return pluralized


@register.simple_tag(takes_context=True)
def get_tab_active_class(context, comparator):
    forloop = context.get('forloop')
    is_first_iteration = forloop.get('first', False) if forloop is not None else False
    active_tab = context.get('active_tab')
    if is_first_iteration and active_tab is None or active_tab == comparator:
        return 'active'
    return ''
