from django import template

register = template.Library()


@register.simple_tag
def pluralize_roles(role, count=None):
    """
    Template tag used to display the plural form of a role. If an optional `count` is specified, then take it into
    account when pluralizing the role

    :param role: The role to pluralize
    :param count: Used to decide if the role should be pluralized if specified. Default: None
    :return: The role, pluralized or just the role if it doesn't meet pluralization criteria.
    """
    SINGULAR_PLURAL_MAPPINGS = {
        'Player': 'Players',
        'Coach': 'Coaches',
        'Referee': 'Referees',
        'Manager': 'Managers'
    }
    if count is None:
        return SINGULAR_PLURAL_MAPPINGS.get(role)
    else:
        return role if count == 1 else SINGULAR_PLURAL_MAPPINGS.get(role)
