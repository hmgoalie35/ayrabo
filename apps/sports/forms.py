from django import forms

from ayrabo.utils.formsets import BaseModelFormSet
from .models import Sport, SportRegistration


class SportRegistrationCreateForm(forms.ModelForm):
    """
    This form can only be used in the admin if the kwarg specifying which sports have already been registered for is not
    specified. We don't know which user was selected in the admin, so trying to figure out what sports they were
    registered for won't work (if we move that logic to the form at some point). There is a unique constraint on the
    model that should help prevent any issues.
    """
    field_order = ('sport', 'role')

    def __init__(self, *args, **kwargs):
        sports_already_registered_for = kwargs.pop('sports_already_registered_for', None)
        super().__init__(*args, **kwargs)
        if sports_already_registered_for:
            self.fields['sport'].queryset = Sport.objects.exclude(id__in=sports_already_registered_for)

    class Meta:
        model = SportRegistration
        fields = ('sport', 'role')


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
