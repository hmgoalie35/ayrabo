"""
A module that contains useful methods for testing
"""
from django.contrib.auth.models import User
from django.db.models import Q

from coaches.tests import CoachFactory
from managers.tests import ManagerFactory
from players.tests import HockeyPlayerFactory
from referees.tests import RefereeFactory


def get_user(username_or_email):
    return User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))


def get_messages(response):
    messages = []
    for msg in response.context['messages']:
        messages.append(msg.message)
    return messages


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
