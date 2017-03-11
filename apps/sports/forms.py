from django import forms
from django.utils.translation import ugettext_lazy as _

from escoresheet.utils.formsets import BaseModelFormSet
from .models import Sport, SportRegistration


class SportRegistrationAdminForm(forms.ModelForm):
    roles = forms.MultipleChoiceField(choices=[(role, role) for role in SportRegistration.ROLES],
                                      widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = SportRegistration
        fields = ['user', 'sport', 'is_complete']
        help_texts = {
            'roles_mask': _(
                    'Use the roles checkboxes to modify this value')
        }


class CreateSportRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """
        Override the constructor to allow for additional kwargs to be passed in.

        :sport_already_registered_for: a list of sport ids the current user has already registered for (so they can't)
          register for that sport again.
        """
        sports_already_registered_for = kwargs.pop('sports_already_registered_for', None)
        super(CreateSportRegistrationForm, self).__init__(*args, **kwargs)
        if sports_already_registered_for is not None:
            self.fields['sport'].queryset = Sport.objects.all().exclude(id__in=sports_already_registered_for)

    roles = forms.MultipleChoiceField(choices=[(role, role) for role in SportRegistration.ROLES],
                                      widget=forms.CheckboxSelectMultiple)

    field_order = ['sport', 'roles']

    class Meta:
        model = SportRegistration
        fields = ['sport']


class SportRegistrationModelFormSet(BaseModelFormSet):
    def clean(self):
        super(SportRegistrationModelFormSet, self).clean()
        sports_already_seen = []
        for form in self.forms:
            sport = form.cleaned_data.get('sport')
            if sport is not None:
                if sport in sports_already_seen:
                    form.add_error('sport', 'Only one form can have {sport} selected. '
                                            'Choose another sport, or remove this form.'.format(sport=sport.name))
                else:
                    sports_already_seen.append(sport)
