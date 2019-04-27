from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from django.core import mail
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from users.models import User
from users.tests import UserFactory


class NewConfirmationEmailViewTests(BaseTestCase):
    url = 'account_new_email_confirmation'

    def post_to_account_new_email_confirmation(self, data):
        return self.client.post(self.format_url(), data, follow=True)

    def setUp(self):
        self.email = 'user@ayrabo.com'
        # In order to have an email confirmation generated, need to POST to the 'account_register' url/view
        self.client.post(reverse('account_register'), {
            'email': self.email,
            'username': self.email,
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'myweakpassword',
            'password2': 'myweakpassword'
        })
        self.user = User.objects.first()
        self.confirmation = EmailConfirmationHMAC(EmailAddress.objects.get(user=self.user))
        # The path that should be redirected to on invalid requests
        self.invalid_request_path = reverse('account_confirm_email', kwargs={'key': self.confirmation.key})
        # The path that should be redirected to on valid requests
        self.valid_request_path = reverse('account_email_verification_sent')

    def test_no_request_path(self):
        response = self.post_to_account_new_email_confirmation({'email': self.user.email})
        self.assertRedirects(response, reverse('home'))

    def test_blank_request_path(self):
        response = self.post_to_account_new_email_confirmation({'email': self.user.email, 'request_path': ''})
        self.assertRedirects(response, reverse('home'))

    def test_no_email_address(self):
        response = self.post_to_account_new_email_confirmation({'request_path': self.invalid_request_path})
        self.assertRedirects(response, self.invalid_request_path)
        self.assertHasMessage(response, 'You must specify an email address.')

    def test_blank_email_address(self):
        response = self.post_to_account_new_email_confirmation({'email': '', 'request_path': self.invalid_request_path})
        self.assertRedirects(response, self.invalid_request_path)
        self.assertHasMessage(response, 'You must specify an email address.')

    def test_nonexistent_email_address(self):
        mail.outbox = []
        invalid_email = 'myinvalidemail@ayrabo.com'
        response = self.post_to_account_new_email_confirmation(
            {'email': invalid_email, 'request_path': self.invalid_request_path})

        error_msg = '{} is not a valid e-mail address or has already been confirmed.'.format(invalid_email)
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
        error_msg = '{} is not a valid e-mail address or has already been confirmed.'.format(self.user.email)
        self.assertHasMessage(response, error_msg)

    def test_existent_email_address(self):
        mail.outbox = []
        response = self.post_to_account_new_email_confirmation(
            {'email': self.user.email, 'request_path': self.valid_request_path})

        success_msg = 'A new confirmation email has been sent to {}.'.format(self.user.email)
        self.assertHasMessage(response, success_msg)
        # Make sure email was actually sent.
        self.assertEqual(len(mail.outbox), 1)
        # Make sure redirect
        self.assertRedirects(response, self.valid_request_path)


class RestrictAllAuthEmailView(BaseTestCase):
    def test_url_redirects_to_home(self):
        response = self.client.get(reverse('account_email'))
        self.assertRedirects(response, reverse('home'))


class PasswordChangeViewTests(BaseTestCase):
    url = 'account_change_password'

    def setUp(self):
        self.user = UserFactory(email='user@ayrabo.com', password='myweakpassword')
        self.login(user=self.user)

    # General
    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.format_url())

    # GET
    def test_get(self):
        response = self.client.get(self.format_url())
        context = response.context

        self.assert_200(response)
        self.assertTemplateUsed('account/password_changed.html')
        self.assertEqual(context.get('active_tab'), 'change-password')
        self.assertEqual(context.get('change_password_link'), self.format_url())
        self.assertFalse(context.get('dynamic'))
        self.assertEqual(context.get('change_password_tab_key'), 'change-password')
        self.assertEqual(context.get('user_obj'), self.user)

    # POST
    def test_post_valid_form(self):
        password = 'mynewpassword'
        data = {'oldpassword': 'myweakpassword', 'password1': password, 'password2': password}
        response = self.client.post(self.format_url(), data=data, follow=True)
        self.assertRedirects(response, reverse('users:detail', kwargs={'pk': self.user.pk}))
        self.assertHasMessage(response, 'Your password has been updated.')

    def test_post_invalid_form(self):
        data = {'oldpassword': 'myweakpassword', 'password1': 'CtpfUE3XHE3y', 'password2': 'def'}
        response = self.client.post(self.format_url(), data=data)
        self.assertFormError(response, 'form', 'password2', 'You must type the same password each time.')
