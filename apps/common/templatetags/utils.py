import json

from django import template

from ayrabo.utils.urls import url_with_query_string as url_with_query_string_util


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


@register.inclusion_tag('includes/copy_to_clipboard_btn.html')
def copy_to_clipboard_btn(text, title='Copy'):
    return {'text': text, 'title': title}


@register.simple_tag
def url_with_query_string(url, **kwargs):
    return url_with_query_string_util(url, **kwargs)
