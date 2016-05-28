from allauth.account import forms as allauth_forms
from django import forms
from escoresheet.utils import remove_form_placeholders


# @TODO set up hooks so that User.objects.create() does the necessary stuff for django all auth to work (create EmailAddress, EmailConfirmation, etc.)
class SignupForm(allauth_forms.SignupForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'autofocus': 'true'}))
    last_name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rearrange order so first name and last name are the first fields the user needs to fill in
        # move_to_end will move to the front if False is specified
        self.fields.move_to_end('last_name', False)
        self.fields.move_to_end('first_name', False)
        remove_form_placeholders(self.fields)

    def clean(self):
        super(SignupForm, self).clean()
        if self.cleaned_data.get('email', None) is not None:
            # Make the username the same as the email
            self.cleaned_data['username'] = self.cleaned_data['email']


class LoginForm(allauth_forms.LoginForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        remove_form_placeholders(self.fields)


class PasswordResetForm(allauth_forms.ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        remove_form_placeholders(self.fields)


class PasswordResetFromKeyForm(allauth_forms.ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetFromKeyForm, self).__init__(*args, **kwargs)
        remove_form_placeholders(self.fields)
