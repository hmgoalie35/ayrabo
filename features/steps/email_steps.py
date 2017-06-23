import re

from behave import *
from django.contrib.sites.models import Site
from django.core import mail


def assert_correct_recipient(context, email, recipient):
    context.test.assertIn(recipient, email.to)


@step('"(?P<username_or_email>[^"]*)" should receive an email with subject "(?P<subject>[^"]*)"')
def step_impl(context, username_or_email, subject):
    last_email = mail.outbox[-1]
    assert_correct_recipient(context, last_email, username_or_email)
    context.test.assertIn(subject, last_email.subject)


@step('"(?P<username_or_email>[^"]*)" follows the email link with subject "(?P<subject>[^"]*)"')
def step_impl(context, username_or_email, subject):
    site = Site.objects.get_current()
    for email in mail.outbox:
        assert_correct_recipient(context, email, username_or_email)
        email_subject = '[{site_name}] {subject}'.format(site_name=site.name, subject=subject)
        if email.subject == email_subject:
            reset_link = re.search(r'(?P<link>https?://.+/)', str(email.body)).group('link')
            context.driver.get(reset_link)


@step('"(?P<username_or_email>[^"]*)" should have (?P<num_emails>no|\d+) emails?')
def step_impl(context, username_or_email, num_emails):
    if num_emails == "no":
        num_emails = 0
    emails = list(filter(lambda e: username_or_email in e.to, mail.outbox))
    context.test.assertEqual(int(num_emails), len(emails))


@step('I follow an invalid password reset link')
def step_impl(context):
    invalid_url = context.get_url('account_reset_password_from_key', uidb36='myinvaliduidb36',
                                  key='new-confirmation-link')
    context.driver.get(invalid_url)


@step('An empty inbox')
def step_impl(context):
    mail.outbox = []
