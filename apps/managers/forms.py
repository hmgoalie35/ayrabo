from django import forms
from django.contrib.auth.models import User

from escoresheet.utils import set_fields_disabled
from escoresheet.utils.form_fields import TeamModelChoiceField
from escoresheet.utils.formsets import BaseModelFormSet
from teams.models import Team
from .models import Manager


class ManagerForm(forms.ModelForm):
    prefix = 'manager'

    def __init__(self, *args, **kwargs):
        """
        Override the constructor to allow for custom kwargs to be passed to this form.

        :sport: The sport to filter teams by
        :read_only_fields: A list of fields that should be disabled in an HTML form. Note that using this will make
            django think the form 'has_changed' when it really hasn't.
        :already_registered_for: ids of teams already registered for
        """
        sport = kwargs.pop('sport', None)
        read_only_fields = kwargs.pop('read_only_fields', None)
        self.user = kwargs.pop('user', None)
        already_registered_for = kwargs.pop('already_registered_for', None)
        super().__init__(*args, **kwargs)

        qs = Team.objects.all().select_related('division')
        if sport is not None:
            qs = qs.filter(division__league__sport=sport)
        if already_registered_for is not None:
            qs = qs.exclude(id__in=already_registered_for)
        self.fields['team'].queryset = qs

        if read_only_fields is not None:
            set_fields_disabled(read_only_fields, self.fields)

    def clean_user(self):
        return self.user

    user = forms.ModelChoiceField(required=False, queryset=User.objects.all(), widget=forms.HiddenInput)
    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = Manager
        fields = ['user', 'team']


class ManagerModelFormSet(BaseModelFormSet):
    def clean(self):
        teams_already_seen = []
        for form in self.forms:
            team = form.cleaned_data.get('team')
            if team is not None:
                if team.id in teams_already_seen:
                    form.add_error('team',
                                   '{} has already been selected. '
                                   'Please choose another team or remove this form.'.format(team.name))
                else:
                    teams_already_seen.append(team.id)
        super().clean()
