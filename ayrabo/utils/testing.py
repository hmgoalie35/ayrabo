import re
from datetime import datetime, timedelta

from django.db.models import Q, QuerySet
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse as drf_reverse
from rest_framework.test import APITestCase

from seasons.tests import SeasonFactory
from users.models import User


def get_user(username_or_email):
    """
    This function is used in *_step.py files, so can't move it to the BaseTestCase class
    """
    return User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))


def _login(client, user, email, password):
    if user:
        return client.force_login(user)
    if email and password:
        return client.login(email=email, password=password)
    raise Exception('You need to provide a user, or email and password')


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
    return {k: v for k, v in kwargs.items() if v is not None}


def to_bool(value):
    if isinstance(value, str):
        value = value.lower()
    return value in [True, 'true']


def comma_separated_string_to_list(string):
    """
    Takes a string of comma separated values and converts it to a list.

    :param string: String of comma separated values
    :return: List of items
    """
    return [item.strip() for item in string.split(',')] if isinstance(string, str) else []


def handle_date(value):
    """
    Util function that helps create dynamic dates in behave tests. Accepts `today` which returns today's date, a normal
    date string that will be returned as is, or a string following this pattern:
    * -1d -> yesterday
    * 1d -> tomorrow
    * 2y -> 2 years in the future
    * -1y -> last year

    :param value: String adhering to the mini DSL this function expects.
    :return: A string representing a date, or a date instance
    """
    today = timezone.now().date()
    if value in ['today', '', None]:
        return today
    re_match = re.fullmatch(r'^(?P<negate>-)?(?P<amount>\d+)(?P<amount_type>[dy])$', value, re.IGNORECASE)
    if re_match is None:
        return value
    negate, amount, amount_type = re_match.groups()
    amount = int(amount)
    if negate is not None:
        amount = -amount
    if amount_type == 'y':
        # Convert to days
        amount *= 365
    return today + timedelta(days=amount)


def handle_time(value):
    """
    Util function that helps create dynamic times in behave tests. Returns the current time or a time equivalent to the
    time string passed in. Ex: 07:00 PM -> time instance for 19:00

    :param value: A time in string format
    :return: Time instance
    """
    time_offset = datetime.strptime(value, '%I:%M %p').time()
    now = timezone.now().timetz()
    if time_offset is not None:
        return now.replace(hour=time_offset.hour, minute=time_offset.minute)
    return now


class BaseTestCase(TestCase):
    fixtures = ['sites.json']

    # Helper methods
    def get_user(self, username_or_email):
        return get_user(username_or_email)

    def format_url(self, **kwargs):
        url = getattr(self, 'url', None)
        if url:
            return reverse(url, kwargs=kwargs)

    def get_login_required_url(self, url):
        return f'{reverse("account_login")}?next={url}'

    def get_session_value(self, key):
        return self.client.session.get(key)

    def login(self, user=None, email=None, password=None):
        return _login(self.client, user, email, password)

    def create_past_current_future_seasons(self, league, teams=None):
        start_date = timezone.now().date()
        kwargs = {
            'league': league
        }
        if teams is not None:
            kwargs.update({'teams': teams})

        past_start_date = start_date - timedelta(days=365)
        future_start_date = start_date + timedelta(days=365)
        past_season = SeasonFactory(
            start_date=past_start_date,
            end_date=start_date - timedelta(days=1),
            **kwargs
        )
        current_season = SeasonFactory(start_date=start_date, end_date=future_start_date, **kwargs)
        future_season = SeasonFactory(
            start_date=future_start_date + timedelta(days=1),
            end_date=future_start_date + timedelta(days=365),
            **kwargs
        )
        return past_season, current_season, future_season

    def _get_messages(self, response):
        return [msg.message for msg in response.context['messages']]

    def _has_message(self, response, msg):
        assert isinstance(msg, str)
        messages = self._get_messages(response)
        return messages, msg in messages

    # Custom assertions
    def assertHasMessage(self, response, msg):
        messages, has_message = self._has_message(response, msg)
        if not has_message:
            self.fail(msg=f'{msg} not found in {messages}')

    def assertNoMessage(self, response, msg):
        _, has_message = self._has_message(response, msg)
        if has_message:
            self.fail(msg=f'{msg} unexpectedly found in messages')

    def assertLoginRequired(self, url):
        response = self.client.get(url)
        self.assertRedirects(response, self.get_login_required_url(url))

    def assertSportNotConfigured(self, url):
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'sport_not_configured_msg.html')

    def assertDictWithQuerySetEqual(self, dictionary, expected):
        cleaned_dict = {}
        for k, v in dictionary.items():
            cleaned_dict[k] = list(v) if isinstance(v, QuerySet) else v
        self.assertDictEqual(cleaned_dict, expected)

    def assert_200(self, response):
        self.assertEqual(response.status_code, 200)

    def assert_404(self, response):
        self.assertEqual(response.status_code, 404)


class BaseAPITestCase(APITestCase):
    fixtures = ['sites.json']

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

    def login(self, user=None, email=None, password=None):
        return _login(self.client, user, email, password)

    # Custom assertions
    def assertAPIError(self, response, status_name, error_message_overrides=None):
        status_code = self.STATUS_CODE_DEFAULTS.get(status_name)
        error_messages = error_message_overrides or self.ERROR_MESSAGE_DEFAULTS.get(status_name)

        self.assertEqual(response.status_code, status_code)
        self.assertDictEqual(response.data, error_messages)

    def assert_200(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def assert_204(self, response):
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
