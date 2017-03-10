from django import forms

from escoresheet.utils import set_fields_disabled
from escoresheet.utils.form_fields import TeamModelChoiceField
from teams.models import Team
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
        """
        sport = kwargs.pop('sport', None)
        read_only_fields = kwargs.pop('read_only_fields', None)
        super(BasePlayerForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['team'].queryset = Team.objects.filter(division__league__sport=sport).select_related('division')
        if read_only_fields is not None:
            set_fields_disabled(read_only_fields, self.fields)


class HockeyPlayerForm(BasePlayerForm):
    prefix = 'hockeyplayer'

    jersey_number = forms.IntegerField(min_value=models.HockeyPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.HockeyPlayer.MAX_JERSEY_NUMBER)

    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = models.HockeyPlayer
        fields = ['team', 'jersey_number', 'position', 'handedness']


class BaseballPlayerForm(BasePlayerForm):
    prefix = 'baseballplayer'

    jersey_number = forms.IntegerField(min_value=models.BaseballPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.BaseballPlayer.MAX_JERSEY_NUMBER)

    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = models.BaseballPlayer
        fields = ['team', 'jersey_number', 'position', 'catches', 'bats']


class BasketballPlayerForm(BasePlayerForm):
    prefix = 'basketballplayer'

    jersey_number = forms.IntegerField(min_value=models.BasketballPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.BasketballPlayer.MAX_JERSEY_NUMBER)

    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = models.BasketballPlayer
        fields = ['team', 'jersey_number', 'position', 'shoots']


# TODO move this and the other modelformset that share same add_fields functionality to base class, inherit from it.
class PlayerModelFormSet(forms.BaseModelFormSet):
    def add_fields(self, form, index):
        super(PlayerModelFormSet, self).add_fields(form, index)
        # The empty form would have value `None`, so default to an invalid form_num for use in the js.
        form_num = index if index is not None else -1
        form.fields['form_num'] = forms.IntegerField(required=False, widget=forms.HiddenInput(
                attrs={'data-form-num': form_num, 'class': 'form-num'}))

    def clean(self):
        super(PlayerModelFormSet, self).clean()
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
