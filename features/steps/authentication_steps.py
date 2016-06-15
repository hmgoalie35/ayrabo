import re

from allauth.account.models import EmailAddress
from behave import *
from django.core import mail
from django.db.models import Q
from generic_steps import find_element
from django.contrib.auth.models import User
from userprofiles.tests.factories.UserProfileFactory import UserProfileFactory


# @TODO use factory
def create_unconfirmed_account(context, user_data, create_userprofile):
    # Doing User.objects.create() will not work because django all auth doesn't know you created a user obj, so need to
    # manually POST to the signup page
    context.test.client.post(context.get_url('account_register'), data=user_data)
    if create_userprofile:
        UserProfileFactory.create(user=User.objects.get(email=user_data['email']))


def confirm_account(context, username_or_email, method='manual'):
    # When method is email, check the mail box and follow the link, otherwise programatically confirm the email address.
    if method == 'email_link':
        email_body = mail.outbox[0].body
        # Django's test client's host is testserver, but we need it to be the current host selenium is using
        # So remove testserver and add in the current host that is being used
        confirmation_link = re.search(r'https?://testserver(?P<link>.*)', str(email_body)).group(
            'link')
        confirmation_link = context.get_url(confirmation_link)
        context.driver.get(confirmation_link)
        confirm_btn = find_element(context, 'confirm_email_btn')
        confirm_btn.click()
    else:
        email_address_obj = EmailAddress.objects.get(
            Q(user__email=username_or_email) | Q(user__username=username_or_email))
        email_address_obj.verified = True
        email_address_obj.save()


def login(context, username_or_email, password, login_method=''):
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

    context.driver.get(context.get_url(login_path))

    fill_in_username_email_step = 'when I fill in "{username_email_field}" with "{username_or_email}"'.format(
        username_email_field=username_email_field, username_or_email=username_or_email)
    fill_in_password_step = 'when I fill in "{password_field}" with "{password}"'.format(
        password_field=password_field,
        password=password)
    press_login_step = 'and I press "{login_btn}"'.format(login_btn=login_btn)

    steps = '''{step_1}\n{step_2}\n{step_3}'''.format(step_1=fill_in_username_email_step,
                                                      step_2=fill_in_password_step,
                                                      step_3=press_login_step)
    context.execute_steps(steps)


def logout(context):
    """
    Logs a user out via the dropdown menu and logout menu item only if a user is logged in
    """
    if 'Logout' in context.driver.page_source:
        steps = '''when I press "account_menu"
               when I press "logout_btn_acct_menu"
               when I press "logout_btn"
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
        user_data = dict(row.as_dict())
        user_data['password1'] = user_data['password']
        user_data['password2'] = user_data['password']
        user_data.pop('password')
        username_or_email = user_data['email']
        create_userprofile = user_data.get('create_userprofile', 'true') in ['True', 'true']
        create_unconfirmed_account(context, user_data, create_userprofile)
        if account_type == 'confirmed':
            confirm_account(context, username_or_email)


@when('I confirm "(?P<username_or_email>.*)" via "(?P<method>.*)"')
def step_impl(context, username_or_email, method):
    confirm_account(context, username_or_email, method)


@when("I follow an invalid email link")
def step_impl(context):
    invalid_url = context.get_url('account_email_verification_sent') + 'myinvalidconfirmationkey'
    context.driver.get(invalid_url)


@step('The following userprofile exists for "(?P<username_or_email>.*)"')
def step_impl(context, username_or_email):
    user = User.objects.get(Q(email=username_or_email) | Q(username=username_or_email))
    for row in context.table:
        userprofile_data = dict(row.as_dict())
        UserProfileFactory.create(user=user, **userprofile_data)

"""

Logging in / out

"""


@given("I am not logged in")
def step_impl(context):
    logout(context)


@step(
    'I login with "(?P<username_or_email>[^"]*)" and "(?P<password>[^"]*)"\s?(?P<optional>via "(?P<login_method>[^"]*)")?')
def step_impl(context, username_or_email, password, optional, login_method):
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


# Permission handling

@step('"(?P<username_or_email>[^"]*)" has the following permissions? "(?P<permissions>[^"]*)"')
def step_impl(context, username_or_email, permissions):
    valid_permissions = ['is_staff', 'is_superuser']
    permissions = permissions.split(' ')
    for permission in permissions:
        user = User.objects.get(
                    Q(email=username_or_email) | Q(username=username_or_email))
        if permission == 'is_staff':
            user.is_staff = True
        elif permission == 'is_superuser':
            user.is_superuser = True
        else:
            raise Exception(
                '{permission} is not a permitted permission. Choose from {permissions}'.format(
                    permission=permission, permissions=valid_permissions))
        user.save()
