"""
A module that contains useful methods for testing
"""


def get_messages(response):
    messages = []
    for msg in response.context['messages']:
        messages.append(msg.message)
    return messages


def is_queryset_in_alphabetical_order(qs, attr_to_test, **kwargs):
    fk = kwargs.get('fk', None)
    qs_count = qs.count()
    qs = list(qs)
    if qs is None or qs_count == 0:
        return True
    if not hasattr(qs[0], attr_to_test):
        raise Exception('Invalid attribute to test %s' % attr_to_test)
    for i in range(qs_count):
        if i + 1 < qs_count:
            obj_one = getattr(qs[i], attr_to_test)
            obj_two = getattr(qs[i + 1], attr_to_test)
            if fk is not None:
                if getattr(obj_one, fk) > getattr(obj_two, fk):
                    return False
            elif obj_one > obj_two:
                return False
    return True
