from crispy_forms.helper import FormHelper
from django import forms

from ayrabo.utils.form_fields import FirstNameLastNameField
from users.models import User


class UserUpdateForm(forms.ModelForm):
    # There might be JavaScript relying on this value, make sure to update any JS accordingly.
    prefix = 'user'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    first_name = FirstNameLastNameField()
    last_name = FirstNameLastNameField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name',)
