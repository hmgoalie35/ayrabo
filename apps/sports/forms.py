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
