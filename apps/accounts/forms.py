from allauth.account import forms as allauth_forms
from django import forms

from escoresheet.utils import remove_form_placeholders, add_autofocus_to_field


class SignupForm(allauth_forms.SignupForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'autofocus': 'true'}))
    last_name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        # Rearrange order so first name and last name are the first fields the user needs to fill in
        # move_to_end will move to the front if False is specified
        self.fields.move_to_end('last_name', False)
        self.fields.move_to_end('first_name', False)
        remove_form_placeholders(self.fields)

    def clean(self):
        super(SignupForm, self).clean()
        if 'email' in self.cleaned_data.keys():
            # Make the username the same as the email
            self.cleaned_data['username'] = self.cleaned_data['email']


class LoginForm(allauth_forms.LoginForm):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super(LoginForm, self).__init__(*args, **kwargs)
        remove_form_placeholders(self.fields)


class PasswordResetForm(allauth_forms.ResetPasswordForm):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        remove_form_placeholders(self.fields)


class PasswordResetFromKeyForm(allauth_forms.ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super(PasswordResetFromKeyForm, self).__init__(*args, **kwargs)
        remove_form_placeholders(self.fields)


class ChangePasswordForm(allauth_forms.ChangePasswordForm):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        remove_form_placeholders(self.fields)
        add_autofocus_to_field(self.fields['oldpassword'])


class AddEmailForm(allauth_forms.AddEmailForm):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super(AddEmailForm, self).__init__(*args, **kwargs)
        remove_form_placeholders(self.fields)
