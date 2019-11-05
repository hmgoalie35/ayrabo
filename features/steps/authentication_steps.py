import re
import time

from behave import *
from django.conf import settings
from django.core import mail


@step(r'I press the email confirmation link')
def step_impl(context):
    email_body = mail.outbox[0].body
    confirmation_link = re.search(r'https?://ayrabo.com(?P<link>.+/)', str(email_body))
    confirmation_link = confirmation_link.group('link')
    context.driver.get(context.get_url(confirmation_link))
    # Not a fan of this, but it seems to work better than the wait for a page refresh step
    time.sleep(3)


@step("I am logged out")
def step_impl(context):
    context.driver.delete_cookie(settings.SESSION_COOKIE_NAME)
    context.driver.get(context.get_url('home'))
    page_source = context.driver.page_source
    context.test.assertIn('Login', page_source)
    context.test.assertNotIn('Logout', page_source)


@step('I login with "(?P<username_or_email>[^"]*)" and "(?P<password>[^"]*)"')
def step_impl(context, username_or_email, password):
    # The 404 page should be pretty lightweight and fast to load
    context.driver.get(context.get_url('/fourohfour'))
    context.test.client.login(username=username_or_email, password=password)
    session_id = context.test.client.cookies[settings.SESSION_COOKIE_NAME]
    context.driver.add_cookie({'name': settings.SESSION_COOKIE_NAME, 'value': session_id.value, 'path': '/'})


@step("I should be logged in")
def step_impl(context):
    page_source = context.driver.page_source
    context.test.assertIn('Account', page_source)
    context.test.assertIn('Logout', page_source)
    context.test.assertNotIn('Login', page_source)


@step("I should be logged out")
def step_impl(context):
    page_source = context.driver.page_source
    context.test.assertIn('Login', page_source)
    context.test.assertNotIn('Logout', page_source)
