"""
A module that contains useful methods for testing
"""
from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse
from rest_framework.reverse import reverse as drf_reverse
from rest_framework.test import APITestCase

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

    def format_url(self, **kwargs):
        url = getattr(self, 'url', None)
        if url:
            return reverse(url, kwargs=kwargs)

    def get_login_required_url(self, url):
        return '{}?next={}'.format(reverse('account_login'), url)

    def login(self, user=None, email=None, password=None):
        if user:
            return self.client.force_login(user)
        if email and password:
            return self.client.login(email=email, password=password)
        return False

    # Custom assertions
    def assertHasMessage(self, response, msg):
        assert isinstance(msg, str)
        messages = [msg.message for msg in response.context['messages']]
        if msg not in messages:
            self.fail(msg='{} not found in {}'.format(msg, messages))

    def assertNoMessage(self, response, msg):
        assert isinstance(msg, str)
        messages = [msg.message for msg in response.context['messages']]
        if msg in messages:
            self.fail(msg='{} unexpectedly found in messages'.format(msg))

    def assert_200(self, response):
        self.assertEqual(response.status_code, 200)

    def assert_404(self, response):
        self.assertEqual(response.status_code, 404)


class BaseAPITestCase(APITestCase):
    ERROR_MESSAGE_DEFAULTS = {
        'not_found': {'detail': 'Not found.'},
        'unauthenticated': {'detail': 'Authentication credentials were not provided.'},
        'permission_denied': {'detail': 'You do not have permission to perform this action.'},
    }

    STATUS_CODE_DEFAULTS = {
        'not_found': 404,
        'unauthenticated': 403,
        'permission_denied': 403,
    }

    def format_url(self, **kwargs):
        url = getattr(self, 'url', None)
        if url:
            return drf_reverse(url, kwargs=kwargs)

    # Custom assertions
    def assertAPIError(self, response, status):
        status_code = self.STATUS_CODE_DEFAULTS.get(status)
        error_messages = self.ERROR_MESSAGE_DEFAULTS.get(status)
        self.assertEqual(response.status_code, status_code)
        self.assertDictEqual(response.data, error_messages)
