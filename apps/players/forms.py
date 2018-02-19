from django import forms

from ayrabo.utils import set_fields_disabled
from ayrabo.utils.form_fields import TeamModelChoiceField
from ayrabo.utils.formsets import BaseModelFormSet
from teams.models import Team
from users.models import User
from . import models


class BasePlayerForm(forms.ModelForm):
    """
    Base form class for all player forms.
    """

    def __init__(self, *args, **kwargs):
        """
        Accepts the following kwargs

        :sport: The sport to filter teams by
        :read_only_fields: List of fields that should be disabled in an HTML form. Note that using this will make
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


class HockeyPlayerForm(BasePlayerForm):
    prefix = 'hockeyplayer'

    jersey_number = forms.IntegerField(min_value=models.HockeyPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.HockeyPlayer.MAX_JERSEY_NUMBER)

    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = models.HockeyPlayer
        fields = ['user', 'team', 'jersey_number', 'position', 'handedness']


class BaseballPlayerForm(BasePlayerForm):
    prefix = 'baseballplayer'

    jersey_number = forms.IntegerField(min_value=models.BaseballPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.BaseballPlayer.MAX_JERSEY_NUMBER)

    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = models.BaseballPlayer
        fields = ['user', 'team', 'jersey_number', 'position', 'catches', 'bats']


class BasketballPlayerForm(BasePlayerForm):
    prefix = 'basketballplayer'

    jersey_number = forms.IntegerField(min_value=models.BasketballPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.BasketballPlayer.MAX_JERSEY_NUMBER)

    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = models.BasketballPlayer
        fields = ['user', 'team', 'jersey_number', 'position', 'shoots']


# Could create a base form with jersey_number and in subclasses extend the meta to add sport specific fields.
class HockeyPlayerUpdateForm(forms.ModelForm):
    class Meta:
        model = models.HockeyPlayer
        fields = ['jersey_number', 'position', 'handedness']


class BaseballPlayerUpdateForm(forms.ModelForm):
    class Meta:
        model = models.BaseballPlayer
        fields = ['jersey_number', 'position', 'catches', 'bats']


class BasketballPlayerUpdateForm(forms.ModelForm):
    class Meta:
        model = models.BasketballPlayer
        fields = ['jersey_number', 'position', 'shoots']


class PlayerModelFormSet(BaseModelFormSet):
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
