import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from django import forms
from django.forms import extras
from django.utils.translation import ugettext_lazy as _

from sports.models import Sport
from .models import UserProfile, RolesMask

YEAR_DIFFERENCE = 20
MAX_AGE = 100


class SelectDateMonthDayYearInitiallyBlankWidget(extras.SelectDateWidget):
    def create_select(self, name, field, value, val, choices, none_value):
        custom_none_value = ()
        if 'year' in field:
            custom_none_value = (0, 'Year')
        elif 'month' in field:
            custom_none_value = (0, 'Month')
        elif 'day' in field:
            custom_none_value = (0, 'Day')
        choices.insert(0, custom_none_value)
        return super(SelectDateMonthDayYearInitiallyBlankWidget, self).create_select(name, field, value, val, choices,
                                                                                     none_value)


class CreateUserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateUserProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
                Field('sports'),
                Field('gender'),
                Field('birthday', wrapper_class='form-inline'),
                Field('height'),
                Field('weight'),
                Field('language'),
                Field('timezone'),
                Div(Submit('create_userprofile_btn', 'Go to next step', css_class='btn btn-success'),
                    css_class='text-center'),
        )

    current_year = datetime.datetime.today().year
    year_range = range(current_year - MAX_AGE, current_year + 1)
    birthday = forms.DateField(
            widget=SelectDateMonthDayYearInitiallyBlankWidget(years=year_range))

    sports = forms.ModelMultipleChoiceField(queryset=Sport.objects.all(),
                                            help_text='Tip: You can search for sports by typing in the input box above')

    field_order = ['sports', 'gender', 'birthday', 'height', 'weight', 'language', 'timezone']

    class Meta:
        model = UserProfile
        fields = ['gender', 'birthday', 'height', 'weight', 'language', 'timezone']
        labels = {
            'weight': _('Weight (in lbs)')
        }


class UpdateUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['height', 'weight', 'language', 'timezone']
        labels = {
            'weight': _('Weight (in lbs)')
        }


class UserProfileAdminForm(forms.ModelForm):
    current_year = datetime.datetime.today().year
    year_range = range(current_year - MAX_AGE, current_year + 1)
    birthday = forms.DateField(
            widget=SelectDateMonthDayYearInitiallyBlankWidget(years=year_range))

    roles = forms.MultipleChoiceField(choices=[(role, role) for role in UserProfile.ROLES],
                                      widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = UserProfile
        fields = ['user', 'gender', 'birthday', 'height', 'weight', 'language', 'timezone', 'is_complete']
        labels = {
            'weight': _('Weight (in lbs)'),
        }
        help_texts = {
            'roles_mask': _(
                    'Use the roles checkboxes to modify this value')
        }


class RolesMaskAdminForm(forms.ModelForm):
    roles = forms.MultipleChoiceField(choices=[(role, role) for role in UserProfile.ROLES],
                                      widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = RolesMask
        fields = ['user', 'sport', 'are_roles_set', 'are_role_objects_created']
        help_texts = {
            'roles_mask': _(
                    'Use the roles checkboxes to modify this value')
        }


class RolesMaskForm(forms.Form):
    roles = forms.MultipleChoiceField(choices=[(role, role) for role in RolesMask.ROLES],
                                      widget=forms.CheckboxSelectMultiple)


