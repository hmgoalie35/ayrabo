from allauth.account.models import EmailConfirmation, EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from escoresheet.testing_utils import get_messages

User = get_user_model()


class NewEmailConfirmationTests(TestCase):
    def post_to_account_new_email_confirmation(self, data):
        return self.client.post(reverse('account_new_email_confirmation'), data, follow=True)

    def setUp(self):
        # In order to have an email confirmation generated, need to POST to the 'account_register' url/view
        self.client.post(reverse('account_register'),
                         {'email': 'user@example.com', 'username': 'user@example.com', 'first_name': 'John',
                          'last_name': 'Doe', 'password1': 'myweakpassword', 'password2': 'myweakpassword'})
        self.user = User.objects.first()
        self.confirmation = EmailConfirmation.objects.get(email_address__email=self.user.email)
        # The path that should be redirected to on invalid requests
        self.invalid_request_path = reverse('account_confirm_email', kwargs={'key': self.confirmation.key})
        # The path that should be redirected to on valid requests
        self.valid_request_path = reverse('account_email_verification_sent')

    def test_no_request_path(self):
        response = self.post_to_account_new_email_confirmation({'email': self.user.email})
        self.assertRedirects(response, '/')

    def test_blank_request_path(self):
        response = self.post_to_account_new_email_confirmation({'email': self.user.email, 'request_path': ''})
        self.assertRedirects(response, '/')

    def test_no_email_address(self):
        response = self.post_to_account_new_email_confirmation({'request_path': self.invalid_request_path})
        self.assertRedirects(response, self.invalid_request_path)
        self.assertIn('You must specify an email address', get_messages(response))

    def test_blank_email_address(self):
        response = self.post_to_account_new_email_confirmation({'email': '', 'request_path': self.invalid_request_path})
        self.assertRedirects(response, self.invalid_request_path)
        self.assertIn('You must specify an email address', get_messages(response))

    def test_nonexistent_email_address(self):
        mail.outbox = []
        invalid_email = 'myinvalidemail@example.com'
        response = self.post_to_account_new_email_confirmation(
                {'email': invalid_email, 'request_path': self.invalid_request_path})

        error_msg = '{email} is not a valid e-mail address or has already been confirmed'.format(email=invalid_email)
        self.assertIn(error_msg, get_messages(response))

        # Make sure email wasn't sent.
        self.assertEqual(len(mail.outbox), 0)

        self.assertRedirects(response, self.invalid_request_path)

    def test_already_confirmed_email_address(self):
        email_address = EmailAddress.objects.get(user=self.user)
        email_address.verified = True
        email_address.primary = True
        email_address.save()
        self.assertTrue(EmailAddress.objects.get(user=self.user).verified)
        response = self.post_to_account_new_email_confirmation(
                {'email': self.user.email, 'request_path': self.invalid_request_path})
        error_msg = '{email} is not a valid e-mail address or has already been confirmed'.format(email=self.user.email)
        self.assertIn(error_msg, get_messages(response))

    def test_existent_email_address(self):
        mail.outbox = []
        response = self.post_to_account_new_email_confirmation(
                {'email': self.user.email, 'request_path': self.valid_request_path})

        success_msg = 'A new confirmation email has been sent to {email}'.format(email=self.user.email)
        self.assertIn(success_msg, get_messages(response))
        # Make sure email was actually sent.
        self.assertEqual(len(mail.outbox), 1)
        # Make sure redirect
        self.assertRedirects(response, self.valid_request_path)
