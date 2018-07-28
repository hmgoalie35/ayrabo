"""
A module that contains useful methods for testing
"""
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.reverse import reverse as drf_reverse
from rest_framework.test import APITestCase

from users.models import User


def get_user(username_or_email):
    """
    This function is used in *_step.py files, so can't move it to the BaseTestCase class
    """
    return User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))


def string_to_kwargs_dict(string):
    """
    Given a string of the form "a=b, c=d" returns a dictionary of key-value pairs. i.e {'a': 'b', 'c': 'd'}
    The purpose is so the return dictionary can be used with ** to pass kwargs to functions.

    :param string: A string of the form "a=b, c=d"
    :return: A dictionary of key value pairs. The key is derived from the left side of = and the value is from the right
      side
    """
    ret_val = {}
    for kwarg in string.split(', '):
        val = kwarg.strip().split('=')
        for i in range(len(val) - 1):
            ret_val[val[i]] = val[i + 1]
    return ret_val


def clean_kwargs(kwargs):
    return {k: v for k, v in kwargs.items() if v}


def to_bool(value):
    if isinstance(value, str):
        value = value.lower()

    return value in [True, 'true']


class BaseTestCase(TestCase):
    # Helper methods
    def get_user(self, username_or_email):
        return get_user(username_or_email)

    def format_url(self, **kwargs):
        url = getattr(self, 'url', None)
        if url:
            return reverse(url, kwargs=kwargs)

    def get_login_required_url(self, url):
        return '{}?next={}'.format(reverse('account_login'), url)

    def get_session_value(self, key):
        return self.client.session.get(key)

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
        'sport_not_configured': {'detail': '{} is not currently configured.'},
        'validation_error': {'detail': ''},
    }

    STATUS_CODE_DEFAULTS = {
        'not_found': status.HTTP_404_NOT_FOUND,
        'unauthenticated': status.HTTP_403_FORBIDDEN,
        'permission_denied': status.HTTP_403_FORBIDDEN,
        'sport_not_configured': status.HTTP_400_BAD_REQUEST,
        'validation_error': status.HTTP_400_BAD_REQUEST,
    }

    def format_url(self, **kwargs):
        url = getattr(self, 'url', None)
        if url:
            return drf_reverse(url, kwargs=kwargs)

    # Custom assertions
    def assertAPIError(self, response, status_name, error_message_overrides=None):
        status_code = self.STATUS_CODE_DEFAULTS.get(status_name)
        error_messages = error_message_overrides or self.ERROR_MESSAGE_DEFAULTS.get(status_name)

        self.assertEqual(response.status_code, status_code)
        self.assertDictEqual(response.data, error_messages)

    def assert_200(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
