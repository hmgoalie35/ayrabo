import re

from allauth.account.models import EmailAddress
from behave import *
from django.contrib.auth.models import User
from django.core import mail
from generic_steps import find_element

user = None
user_password = None


def create_confirmed_account(context):
    create_unconfirmed_account(context)
    confirm_account(context)


def create_unconfirmed_account(context):
    # Doing User.objects.create() will not work because django all auth doesn't know you created a user obj, so need to
    # manually POST to the signup page
    user_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'islanders1980',
        'email': 'user@example.com',
        'password1': 'myweakpassword',
        'password2': 'myweakpassword'
    }
    context.test.client.post(context.get_url('account_register'), data=user_data)
    global user
    user = User.objects.get(email='user@example.com')
    global user_password
    user_password = 'myweakpassword'


def confirm_account(context, method='manual'):
    # When method is email, check the mail box and follow the link, otherwise programatically confirm the email address.
    if method == 'email':
        email_body = mail.outbox[0].body
        # Django's test client's host is testserver, but we need it to be the current host selenium is using
        # So remove testserver and add in the current host that is being used
        confirmation_link = re.search(r'https?://testserver(?P<link>.*)', str(email_body)).group('link')
        confirmation_link = context.get_url(confirmation_link)
        context.driver.get(confirmation_link)
        confirm_btn = find_element(context, 'confirm_email_btn')
        confirm_btn.click()
    else:
        email_address_obj = EmailAddress.objects.get(user=user)
        email_address_obj.verified = True
        email_address_obj.save()


def login(context, login_method='', email='', password=''):
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

    fill_in_username_email_step = 'when I fill in "{username_email_field}" with "{email}"'.format(
            username_email_field=username_email_field, email=user.email if len(email) == 0 else email)
    fill_in_password_step = 'when I fill in "{password_field}" with "{password}"'.format(password_field=password_field,
                                                                                         password=user_password if len(
                                                                                             password) == 0 else password)
    press_login_step = 'and I press "{login_btn}"'.format(login_btn=login_btn)

    steps = '''{step_1}\n{step_2}\n{step_3}'''.format(step_1=fill_in_username_email_step, step_2=fill_in_password_step,
                                                      step_3=press_login_step)
    context.execute_steps(steps)


"""

Account management

"""


@given("I have a confirmed account")
def step_impl(context):
    create_confirmed_account(context)


@given("I have an unconfirmed account")
def step_impl(context):
    create_unconfirmed_account(context)


@when('I confirm my account via "(?P<method>.*)"')
def step_impl(context, method):
    confirm_account(context, method)


@when("I follow an invalid email link")
def step_impl(context):
    invalid_url = context.get_url('account_email_verification_sent') + 'myinvalidconfirmationkey'
    context.driver.get(invalid_url)


"""

Logging in / out

"""


@given("I am not logged in")
def step_impl(context):
    context.driver.get(context.get_url('home'))
    context.test.client.logout()
    context.test.assertIn('Login', context.driver.page_source)
    context.test.assertNotIn('Logout', context.driver.page_source)


@when('I login with valid credentials\s*(?P<optional>via "(?P<login_method>.*)")?')
def step_impl(context, optional, login_method):
    login(context, login_method)


@when('I login with an invalid "(?P<method>.*)"')
def step_impl(context, method):
    if method == 'email':
        login(context, email='myinvalidemail@testing.com')
    elif method == 'password':
        login(context, password='myinvalidpassword')


@then("I should be logged in")
def step_impl(context):
    context.test.assertIn('Account', context.driver.page_source)
    context.test.assertIn('Logout', context.driver.page_source)
    context.test.assertNotIn('Login', context.driver.page_source)


@then("I should not be logged in")
def step_impl(context):
    context.test.assertIn('Login', context.driver.page_source)
    context.test.assertNotIn('Logout', context.driver.page_source)
