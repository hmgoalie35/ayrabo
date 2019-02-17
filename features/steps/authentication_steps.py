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


def login(context, username_or_email, password, login_method=None):
    # If no login method is specified, force authenticate the user so don't need to do extra behave steps.
    if login_method:
        # Defaults are for logging in via login page, not the navbar
        login_path = 'account_login'
        username_email_field = 'id_login'
        password_field = 'id_password'
        login_btn = 'login_main'
        if login_method == 'navbar':
            login_path = 'home'
            username_email_field = 'id_login_navbar'
            password_field = 'id_password_navbar'
            login_btn = 'login_navbar'

        step1 = 'when I fill in "{}" with "{}"'.format(username_email_field, username_or_email)
        step2 = 'when I fill in "{}" with "{}"'.format(password_field, password)
        step3 = 'and I press "{}"'.format(login_btn)
        steps = '{}\n{}\n{}'.format(step1, step2, step3)

        context.driver.get(context.get_url(login_path))
        context.execute_steps(steps)
    else:
        # The 404 page should be pretty lightweight and fast to load
        context.driver.get(context.get_url('/fourohfour'))
        context.test.client.login(username=username_or_email, password=password)
        session_id = context.test.client.cookies[settings.SESSION_COOKIE_NAME]
        context.driver.add_cookie({'name': settings.SESSION_COOKIE_NAME, 'value': session_id.value, 'path': '/'})


def logout(context):
    """
    Logs a user out via the dropdown menu and logout menu item only if a user is logged in
    """
    if 'Logout' in context.driver.page_source:
        steps = '''when I press "account_menu"
               when I press "logout_btn_acct_menu"
        '''
        context.execute_steps(steps)
    context.driver.get(context.get_url('home'))
    context.test.assertIn('Login', context.driver.page_source)
    context.test.assertNotIn('Logout', context.driver.page_source)


"""

Account management

"""


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


@when('I confirm "(?P<username_or_email>.*)" via "(?P<method>.*)"')
def step_impl(context, username_or_email, method):
    confirm_account(context, username_or_email, method)
    # Not a fan of this, but it seems to work better than the wait for a page refresh step
    time.sleep(3)


@when("I follow an invalid email link")
def step_impl(context):
    invalid_url = context.get_url('account_email_verification_sent') + 'myinvalidconfirmationkey'
    context.driver.get(invalid_url)


@step('The following userprofile exists for "(?P<username_or_email>.*)"')
def step_impl(context, username_or_email):
    user = get_user(username_or_email)
    for row in context.table:
        userprofile_data = row.as_dict()
        UserProfileFactory.create(user=user, **userprofile_data)


"""

Logging in / out

"""


@given("I am not logged in")
def step_impl(context):
    logout(context)


@step('I login with "(?P<username_or_email>[^"]*)" and "(?P<password>[^"]*)"')  # noqa
def step_impl(context, username_or_email, password):
    login(context, username_or_email, password, None)


@step('I login with "(?P<username_or_email>[^"]*)" and "(?P<password>[^"]*)" via "(?P<login_method>[^"]*)"')
def step_impl(context, username_or_email, password, login_method):
    login(context, username_or_email, password, login_method)


@then("I should be logged in")
def step_impl(context):
    context.test.assertIn('Account', context.driver.page_source)
    context.test.assertIn('Logout', context.driver.page_source)
    context.test.assertNotIn('Login', context.driver.page_source)


@then("I should not be logged in")
def step_impl(context):
    context.test.assertIn('Login', context.driver.page_source)
    context.test.assertNotIn('Logout', context.driver.page_source)


@when("I logout")
def step_impl(context):
    logout(context)


"""

Permission handling

"""


@step('"(?P<username_or_email>[^"]*)" has the following permissions? "(?P<permissions>[^"]*)"')
def step_impl(context, username_or_email, permissions):
    valid_permissions = ['is_staff', 'is_superuser']
    permissions = permissions.split(' ')
    user = get_user(username_or_email)
    for permission in permissions:
        if permission in valid_permissions:
            setattr(user, permission, True)
        else:
            raise Exception(
                '{} is not a valid permission. Choose from {}'.format(permission, valid_permissions))
        user.save()
