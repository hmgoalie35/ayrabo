from behave import *
from django.core import mail
import re
from django.contrib.sites.models import Site


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
        if email.subject == "[%s] %s" % (site.name, subject):
            reset_link = re.search(r'https?://{host}(?P<link>.*)'.format(host=site.domain), str(email.body)).group('link')
            reset_link = context.get_url(reset_link)
            context.driver.get(reset_link)


@step('"(?P<username_or_email>[^"]*)" should have (?P<num_emails>no|\d+) emails?')
def step_impl(context, username_or_email, num_emails):
    count = 0
    for email in mail.outbox:
        if username_or_email in email.to:
            count += 1
    if num_emails == "no":
        num_emails = 0
    context.test.assertEqual(int(num_emails), count)


@step('I follow an invalid password reset link')
def step_impl(context):
    invalid_url = context.get_url('account_reset_password_from_key', uidb36='myinvaliduidb36', key='myinvalidkey')
    context.driver.get(invalid_url)


@step('An empty inbox')
def step_impl(context):
    mail.outbox = []
