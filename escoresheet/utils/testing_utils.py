"""
A module that contains useful methods for testing
"""
from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase

from coaches.tests import CoachFactory
from managers.tests import ManagerFactory
from players.tests import HockeyPlayerFactory
from referees.tests import RefereeFactory


def get_user(username_or_email):
    """
    This function is used in *_step.py files, so can't move it to the BaseTestCase class
    """
    return User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))


class BaseTestCase(TestCase):
    # Helper methods
    def get_user(self, username_or_email):
        return get_user(username_or_email)

    def create_related_objects(self, **kwargs):
        player_args = kwargs.pop('player_args', {})
        coach_args = kwargs.pop('coach_args', {})
        referee_args = kwargs.pop('referee_args', {})
        manager_args = kwargs.pop('manager_args', {})

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

    # Custom assertions
    def assertHasMessage(self, response, msg):
        assert isinstance(msg, str)
        messages = [msg.message for msg in response.context['messages']]
        if msg not in messages:
            self.fail(msg='{} not found in messages'.format(msg))

    def assertNoMessage(self, response, msg):
        assert isinstance(msg, str)
        messages = [msg.message for msg in response.context['messages']]
        if msg in messages:
            self.fail(msg='{} unexpectedly found in messages'.format(msg))
