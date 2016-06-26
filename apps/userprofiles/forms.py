import datetime

from django import forms
from django.forms import extras
from django.utils.translation import ugettext_lazy as _

from .models import UserProfile

YEAR_DIFFERENCE = 20
MAX_AGE = 100


class CreateUserProfileForm(forms.ModelForm):
    current_year = datetime.datetime.today().year
    birthday = forms.DateField(initial=datetime.datetime.today().replace(year=current_year - YEAR_DIFFERENCE),
                               widget=extras.SelectDateWidget(years=range(current_year - MAX_AGE, current_year)))

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
    birthday = forms.DateField(initial=datetime.datetime.today().replace(year=current_year - YEAR_DIFFERENCE),
                               widget=extras.SelectDateWidget(years=range(current_year - MAX_AGE, current_year)))

    class Meta:
        model = UserProfile
        fields = ['user', 'roles_mask', 'gender', 'birthday', 'height', 'weight', 'language', 'timezone']
        labels = {
            'weight': _('Weight (in lbs)'),
        }
        help_texts = {
            'roles_mask': _(
                    'Ask Harris how to convert roles_mask from int to list of strings and vice versa or see the'
                    ' set_roles function in userprofiles/models.py')
        }
