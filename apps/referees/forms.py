from django import forms

from ayrabo.utils import set_fields_disabled
from ayrabo.utils.formsets import BaseModelFormSet
from leagues.models import League
from users.models import User
from .models import Referee


class RefereeForm(forms.ModelForm):
    prefix = 'referee'

    def __init__(self, *args, **kwargs):
        """
        Override the constructor to allow for custom kwargs to be passed to this form.

        :sport: The sport to filter teams by
        :read_only_fields: A list of fields that should be disabled in an HTML form. Note that using this will make
            django think the form 'has_changed' when it really hasn't.
        :already_registered_for: ids of leagues already registered for
        """
        sport = kwargs.pop('sport', None)
        read_only_fields = kwargs.pop('read_only_fields', None)
        self.user = kwargs.pop('user', None)
        already_registered_for = kwargs.pop('already_registered_for', None)
        super().__init__(*args, **kwargs)

        qs = League.objects.all().select_related('sport')
        if sport is not None:
            qs = qs.filter(sport=sport)
        if already_registered_for is not None:
            qs = qs.exclude(id__in=already_registered_for)
        self.fields['league'].queryset = qs

        if read_only_fields is not None:
            set_fields_disabled(read_only_fields, self.fields)

    def clean_user(self):
        return self.user

    user = forms.ModelChoiceField(required=False, queryset=User.objects.all(), widget=forms.HiddenInput)

    class Meta:
        model = Referee
        fields = ['user', 'league']


class RefereeModelFormSet(BaseModelFormSet):  # pragma: no cover
    def clean(self):
        leagues_already_seen = []
        for form in self.forms:
            league = form.cleaned_data.get('league')
            if league is not None:
                if league.id in leagues_already_seen:
                    form.add_error('league',
                                   '{} has already been selected. '
                                   'Please choose another league or remove this form.'.format(league.name))
                else:
                    leagues_already_seen.append(league.id)
        super().clean()
