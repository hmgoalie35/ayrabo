from behave import *
from django.core import mail
import re
from allauth.account.models import EmailConfirmation, EmailAddress
from generic_steps import find_element


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


def confirm_account(context, method='manual', valid_email=True):
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
        import pdb; pdb.set_trace()


@given("I am not logged in")
def step_impl(context):
    context.driver.get(context.get_url('home'))
    context.test.client.logout()
    context.test.assertIn('Login', context.driver.page_source)
    context.test.assertNotIn('Logout', context.driver.page_source)


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
