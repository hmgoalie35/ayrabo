"""
A module that contains useful methods for testing
"""
from coaches.tests import CoachFactory
from managers.tests.factories.ManagerFactory import ManagerFactory
from players.tests.factories.PlayerFactory import HockeyPlayerFactory
from referees.tests.factories.RefereeFactory import RefereeFactory


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


def create_related_objects(**kwargs):
    player_args = kwargs.pop('player_args', None)
    coach_args = kwargs.pop('coach_args', None)
    referee_args = kwargs.pop('referee_args', None)
    manager_args = kwargs.pop('manager_args', None)

    player = coach = referee = manager = None

    if player_args:
        player = HockeyPlayerFactory(**player_args)
    if coach_args:
        coach = CoachFactory(**coach_args)
    if referee_args:
        referee = RefereeFactory(**referee_args)
    if manager_args:
        manager = ManagerFactory(**manager_args)

    return player, coach, referee, manager
