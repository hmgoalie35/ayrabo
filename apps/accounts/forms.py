from allauth.account import forms as allauth_forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, HTML, Layout, Submit
from django import forms
from django.contrib.auth.password_validation import password_validators_help_texts

from ayrabo.utils import add_autofocus_to_field, remove_form_placeholders
from ayrabo.utils.form_fields import FirstNameLastNameField


PASSWORD_GUIDELINES_HTML = """
<span
    class="password-guidelines clickable pull-right"
    data-toggle="modal"
    data-target="#password_guidelines">

    <span
        data-toggle="tooltip"
        data-placement="left"
        title="Password guidelines"
        class="fa fa-info-circle">
    </span>
</span>
"""


class SignupForm(allauth_forms.SignupForm):
    first_name = FirstNameLastNameField(widget=forms.TextInput(attrs={'autofocus': 'true'}))
    last_name = FirstNameLastNameField()

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        # Rearrange order so first name and last name are the first fields the user needs to fill in
        # move_to_end will move to the front if False is specified
        self.fields.move_to_end('last_name', False)
        self.fields.move_to_end('first_name', False)
        remove_form_placeholders(self.fields)

        self.password_validator_help_text = password_validators_help_texts()

        self.helper = FormHelper()
        # csrf token manually included in template
        self.helper.disable_csrf = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('first_name'),
            Field('last_name'),
            Field('email'),
            HTML(PASSWORD_GUIDELINES_HTML),
            Field('password1'),
            Field('password2'),
            HTML('<br>'),
            Div(Submit('id_submit', 'Register', css_class='btn btn-success', css_id="id_submit"),
                css_class='text-center'),
            HTML('<br>'),
        )

    def clean(self):
        super(SignupForm, self).clean()
        if 'email' in self.cleaned_data.keys():
            # Make the username the same as the email
            self.cleaned_data['username'] = self.cleaned_data['email']


class LoginForm(allauth_forms.LoginForm):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super(LoginForm, self).__init__(*args, **kwargs)
        remove_form_placeholders(self.fields)

        self.password_validator_help_text = password_validators_help_texts()

        self.helper = FormHelper()
        # csrf token manually included in template
        self.helper.disable_csrf = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('login'),
            HTML(PASSWORD_GUIDELINES_HTML),
            Field('password'),
            HTML('<br>'),
            Div(Submit('login_main', 'Login',
                       css_class='btn btn-success', css_id="login_main"),
                css_class='text-center'),
        )


class PasswordResetForm(allauth_forms.ResetPasswordForm):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        remove_form_placeholders(self.fields)


class PasswordResetFromKeyForm(allauth_forms.ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super(PasswordResetFromKeyForm, self).__init__(*args, **kwargs)
        remove_form_placeholders(self.fields)

        self.password_validator_help_text = password_validators_help_texts()

        self.helper = FormHelper()
        # csrf token manually included in template
        self.helper.disable_csrf = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            HTML(PASSWORD_GUIDELINES_HTML),
            Field('password1'),
            Field('password2'),
            HTML('<br>'),
            Div(Submit('reset_password_btn', 'Reset password',
                       css_class='btn btn-success', css_id="reset_password_btn"),
                css_class='text-center'),
            HTML('<br>'),
        )


class ChangePasswordForm(allauth_forms.ChangePasswordForm):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        remove_form_placeholders(self.fields)
        add_autofocus_to_field(self.fields['oldpassword'])

        self.password_validator_help_text = password_validators_help_texts()

        self.helper = FormHelper()
        # csrf token manually included in template
        self.helper.disable_csrf = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('oldpassword'),
            HTML(PASSWORD_GUIDELINES_HTML),
            Field('password1'),
            Field('password2'),
            HTML('<br>'),
            Div(Submit('change_password_btn', 'Change password',
                       css_class='btn btn-success', css_id="change_password_btn"),
                css_class='text-center'),
            HTML('<br>'),
        )


class AddEmailForm(allauth_forms.AddEmailForm):
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super(AddEmailForm, self).__init__(*args, **kwargs)
        remove_form_placeholders(self.fields)
