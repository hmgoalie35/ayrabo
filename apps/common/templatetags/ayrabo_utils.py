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
