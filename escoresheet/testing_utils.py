"""
A module that contains useful methods for testing
"""


def get_messages(response):
    messages = []
    for msg in response.context['messages']:
        messages.append(msg.message)
    return messages


def is_queryset_in_alphabetical_order(qs, attr_to_test):
    qs = list(qs)
    if qs is None or len(qs) == 0:
        return True
    if not hasattr(qs[0], attr_to_test):
        raise Exception('Invalid attribute to test %s' % attr_to_test)
    for i in range(len(qs) - 1):
        if getattr(qs[i], attr_to_test) > getattr(qs[i+1], attr_to_test):
            return False
    return True
