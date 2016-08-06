from django import forms
from django.utils.translation import ugettext_lazy as _

from . import models


class SportRegistrationAdminForm(forms.ModelForm):
    roles = forms.MultipleChoiceField(choices=[(role, role) for role in models.SportRegistration.ROLES],
                                      widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = models.SportRegistration
        fields = ['user', 'sport', 'is_complete']
        help_texts = {
            'roles_mask': _(
                    'Use the roles checkboxes to modify this value')
        }


class CreateSportRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        sports_already_registered_for = kwargs.pop('sports_already_registered_for', None)
        super(CreateSportRegistrationForm, self).__init__(*args, **kwargs)
        if sports_already_registered_for is not None:
            self.fields['sport'].queryset = models.Sport.objects.all().exclude(id__in=sports_already_registered_for)

    roles = forms.MultipleChoiceField(choices=[(role, role) for role in models.SportRegistration.ROLES],
                                      widget=forms.CheckboxSelectMultiple)

    field_order = ['sport', 'roles']

    class Meta:
        model = models.SportRegistration
        fields = ['sport']
