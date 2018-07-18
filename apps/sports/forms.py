from django import forms

from ayrabo.utils.formsets import BaseFormSet
from .models import Sport, SportRegistration


class SportRegistrationCreateForm(forms.Form):
    """
    This form can only be used in the admin if the kwarg specifying which sports have already been registered for is not
    specified. We don't know which user was selected in the admin, so trying to figure out what sports they were
    registered for won't work (if we move that logic to the form at some point). There is a unique constraint on the
    model that should help prevent any issues.
    """

    def __init__(self, *args, **kwargs):
        sports_already_registered_for = kwargs.pop('sports_already_registered_for', None)
        super().__init__(*args, **kwargs)
        if sports_already_registered_for:
            self.fields['sport'].queryset = Sport.objects.exclude(id__in=sports_already_registered_for)

    sport = forms.ModelChoiceField(queryset=Sport.objects.all())
    roles = forms.MultipleChoiceField(choices=SportRegistration.ROLE_CHOICES, widget=forms.CheckboxSelectMultiple)

    class Meta:
        fields = ('sport', 'roles')


class SportRegistrationFormSet(BaseFormSet):
    def clean(self):
        super().clean()
        sports_already_seen = []
        for form in self.forms:
            sport = form.cleaned_data.get('sport')
            if sport is None:
                continue
            if sport in sports_already_seen:
                error = '{} has already been selected. Choose another sport or remove this form.'.format(sport.name)
                form.add_error('sport', error)
            else:
                sports_already_seen.append(sport)
