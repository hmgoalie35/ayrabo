from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms

from ayrabo.utils.form_fields import BirthdayField, WeightField
from .models import UserProfile


class UserProfileCreateUpdateForm(forms.ModelForm):
    # There might be JavaScript relying on this value, make sure to update any JS accordingly.
    prefix = 'user_profile'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Field('gender'),
            # This makes the birthday select tags inline
            Field('birthday', wrapper_class='form-inline'),
            Field('height'),
            Field('weight'),
            Field('timezone')
        )

    birthday = BirthdayField()
    weight = WeightField(min_value=UserProfile.MIN_WEIGHT, max_value=UserProfile.MAX_WEIGHT)

    class Meta:
        model = UserProfile
        fields = ['gender', 'birthday', 'height', 'weight', 'timezone']


class UserProfileAdminForm(forms.ModelForm):
    birthday = BirthdayField()
    weight = WeightField(min_value=UserProfile.MIN_WEIGHT, max_value=UserProfile.MAX_WEIGHT)

    class Meta:
        model = UserProfile
        fields = ['user', 'gender', 'birthday', 'height', 'weight', 'timezone', 'language']
