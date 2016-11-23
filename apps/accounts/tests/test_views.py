from allauth.account.models import EmailConfirmationHMAC, EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from escoresheet.utils import BaseTestCase

User = get_user_model()


class NewEmailConfirmationTests(BaseTestCase):
    def post_to_account_new_email_confirmation(self, data):
        return self.client.post(reverse('account_new_email_confirmation'), data, follow=True)

    def setUp(self):
        self.email = 'user@example.com'
        # In order to have an email confirmation generated, need to POST to the 'account_register' url/view
        self.client.post(reverse('account_register'),
                         {'email': self.email, 'username': self.email, 'first_name': 'John',
                          'last_name': 'Doe', 'password1': 'myweakpassword', 'password2': 'myweakpassword'})
        self.user = User.objects.first()
        self.confirmation = EmailConfirmationHMAC(EmailAddress.objects.get(user=self.user))
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
        self.assertHasMessage(response, 'You must specify an email address')

    def test_blank_email_address(self):
        response = self.post_to_account_new_email_confirmation({'email': '', 'request_path': self.invalid_request_path})
        self.assertRedirects(response, self.invalid_request_path)
        self.assertHasMessage(response, 'You must specify an email address')

    def test_nonexistent_email_address(self):
        mail.outbox = []
        invalid_email = 'myinvalidemail@example.com'
        response = self.post_to_account_new_email_confirmation(
                {'email': invalid_email, 'request_path': self.invalid_request_path})

        error_msg = '{email} is not a valid e-mail address or has already been confirmed'.format(email=invalid_email)
        self.assertHasMessage(response, error_msg)

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
        self.assertHasMessage(response, error_msg)

    def test_existent_email_address(self):
        mail.outbox = []
        response = self.post_to_account_new_email_confirmation(
                {'email': self.user.email, 'request_path': self.valid_request_path})

        success_msg = 'A new confirmation email has been sent to {email}'.format(email=self.user.email)
        self.assertHasMessage(response, success_msg)
        # Make sure email was actually sent.
        self.assertEqual(len(mail.outbox), 1)
        # Make sure redirect
        self.assertRedirects(response, self.valid_request_path)


class RestrictAllAuthEmailView(BaseTestCase):
    def test_url_redirects_to_home(self):
        response = self.client.get(reverse('account_email'))
        self.assertRedirects(response, reverse('home'))
