import re
import time

from allauth.account.models import EmailAddress
from behave import *
from django.conf import settings
from django.core import mail

from accounts.tests import EmailAddressFactory
from ayrabo.utils.testing import get_user
from userprofiles.tests import UserProfileFactory
from users.tests import UserFactory


def create_unconfirmed_account(user_data, create_userprofile):
    """
    Creates an unconfirmed user account with the specified `user_data`. Also optionally creates a userprofile.

    :param user_data: Dictionary of key value pairs for username, email, etc.
    :param create_userprofile: Whether to create a userprofile or not.
    """
    # userprofile kwarg prevents the userfactory from creating a userprofile
    user_data['userprofile'] = None
    if not user_data.get('id'):
        user_data.pop('id', None)
    user = UserFactory(**user_data)
    email = EmailAddressFactory(user=user, email=user_data['email'], verified=False, primary=False)
    email.send_confirmation()

    if create_userprofile:
        UserProfileFactory(user=user)


def confirm_account(context, username_or_email, method='manual'):
    """
    Confirms an account via an email link, or programmatically.

    :method: `manual` or `email_link` -- Self explanatory
    """
    if method == 'email_link':
        email_body = mail.outbox[0].body
        confirmation_link = re.search(r'https?://ayrabo.com(?P<link>.+/)', str(email_body)).group('link')
        context.driver.get(context.get_url(confirmation_link))
    else:
        email_address_obj = EmailAddress.objects.get(user=get_user(username_or_email))
        email_address_obj.verified = True
        email_address_obj.save()


@step("The following (?P<account_type>confirmed|unconfirmed) user accounts? exists?")
def step_impl(context, account_type):
    for row in context.table:
        user_data = row.as_dict()
        username_or_email = user_data['email']
        create_userprofile = user_data.get('create_userprofile', 'true') in ['True', 'true']
        user_data.pop('create_userprofile') if 'create_userprofile' in user_data.keys() else None
        create_unconfirmed_account(user_data, create_userprofile)
        if account_type == 'confirmed':
            confirm_account(context, username_or_email)


@step('I confirm "(?P<username_or_email>.*)" via "(?P<method>.*)"')
def step_impl(context, username_or_email, method):
    confirm_account(context, username_or_email, method)
    # Not a fan of this, but it seems to work better than the wait for a page refresh step
    time.sleep(3)


@step("I follow an invalid email link")
def step_impl(context):
    invalid_url = context.get_url('account_email_verification_sent') + 'myinvalidconfirmationkey'
    context.driver.get(invalid_url)


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
