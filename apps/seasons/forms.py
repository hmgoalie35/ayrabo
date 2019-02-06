from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout
from django import forms
from django.contrib.admin import widgets
from django.core.exceptions import ValidationError

from ayrabo.utils.form_fields import (
    PlayerModelMultipleChoiceField,
    SeasonModelChoiceField,
    TeamModelChoiceField,
    TeamModelMultipleChoiceField,
)
from ayrabo.utils.mixins import DisableFormFieldsMixin
from players.models import HockeyPlayer
from teams.models import Team
from .models import HockeySeasonRoster, Season


class SeasonAdminForm(forms.ModelForm):
    teams = TeamModelMultipleChoiceField(queryset=Team.objects.select_related('division').all(),
                                         widget=widgets.FilteredSelectMultiple('Teams', False))

    class Meta:
        model = Season
        fields = ['league', 'start_date', 'end_date', 'teams']

    def clean(self):
        super().clean()
        league = self.cleaned_data.get('league', None)
        teams = self.cleaned_data.get('teams', [])
        errors = {'teams': []}
        if league and teams:
            for team in teams:
                if team.division.league_id != league.id:
                    errors['teams'].append(
                        'The team specified ({team_name}) does not belong to {league}'.format(
                            team_name=team.name, league=league.name))

            if errors['teams']:
                raise ValidationError(errors)


class HockeySeasonRosterAdminForm(forms.ModelForm):
    """
    Custom admin form that optimizes db access for certain model fields.
    """

    sport_name = 'Hockey'

    season = SeasonModelChoiceField(
        queryset=Season.objects.filter(league__sport__name__icontains=sport_name).select_related(
            'league'))
    team = TeamModelChoiceField(
        queryset=Team.objects.filter(division__league__sport__name__icontains=sport_name).select_related(
            'division'))

    players = forms.ModelMultipleChoiceField(queryset=HockeyPlayer.objects.active().select_related('user'),
                                             widget=widgets.FilteredSelectMultiple(verbose_name='Players',
                                                                                   is_stacked=False))

    class Meta:
        model = HockeySeasonRoster
        fields = '__all__'


class HockeySeasonRosterCreateUpdateForm(DisableFormFieldsMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        # When being used as an update form, just grab the team from the instance.
        if not self.team:
            self.team = self.instance.team

        self.helper = FormHelper()
        # csrf token manually included in template
        self.helper.disable_csrf = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'name',
            'season',
            'players',
            Div(
                'default',
                css_class='text-center'
            )
        )

        league = self.team.division.league

        self.fields['season'].queryset = Season.objects.filter(league=league).select_related('league')
        self.fields['players'].queryset = HockeyPlayer.objects.active().filter(team=self.team).select_related('user')

    # querysets are overridden in form constructor anyway
    season = SeasonModelChoiceField(queryset=Season.objects.none())
    players = PlayerModelMultipleChoiceField(position_field='position', queryset=HockeyPlayer.objects.none())

    class Meta:
        model = HockeySeasonRoster
        fields = ['name', 'season', 'players', 'default']
