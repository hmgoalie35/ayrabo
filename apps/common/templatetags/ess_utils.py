from django import template

register = template.Library()

SINGULAR_PLURAL_MAPPINGS = {
    'Player': 'Players',
    'Coach': 'Coaches',
    'Referee': 'Referees',
    'Manager': 'Managers',
    'Scorekeeper': 'Scorekeepers'
}


@register.simple_tag
def pluralize_roles(role, count=None):
    """
    Template tag used to display the plural form of a role. If an optional `count` is specified, then take it into
    account when pluralizing the role

    :param role: The role to pluralize
    :param count: Used to decide if the role should be pluralized if specified. Default: None
    :return: The role, pluralized or just the role if it doesn't meet pluralization criteria.
    """
    if count is None:
        return SINGULAR_PLURAL_MAPPINGS.get(role)
    else:
        return role if count == 1 else SINGULAR_PLURAL_MAPPINGS.get(role)


@register.filter
def get(dictionary, key):
    return dictionary.get(key)


@register.filter
def pluralize_role(value, role):
    role_pluralized = SINGULAR_PLURAL_MAPPINGS.get(role, None)
    return '{}{}'.format(value, role_pluralized.lower() if role_pluralized is not None else role_pluralized)
