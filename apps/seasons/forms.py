import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.contrib.admin import widgets
from django.core.exceptions import ValidationError

from ayrabo.utils import set_fields_disabled
from ayrabo.utils.form_fields import SeasonModelChoiceField, TeamModelChoiceField, TeamModelMultipleChoiceField
from players.models import HockeyPlayer
from teams.models import Team
from .models import Season, HockeySeasonRoster


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
                            team_name=team.name, league=league.full_name))

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


class HockeySeasonRosterCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop('team')

        super().__init__(*args, **kwargs)

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
        today = datetime.date.today()

        self.fields['season'].queryset = Season.objects.filter(league=league).exclude(
            end_date__lt=today).select_related('league')
        self.fields['players'].queryset = HockeyPlayer.objects.active().filter(team=self.team).select_related('user')

    # querysets are overridden in form constructor anyway
    season = SeasonModelChoiceField(queryset=Season.objects.none())
    players = forms.ModelMultipleChoiceField(queryset=HockeyPlayer.objects.none())

    class Meta:
        model = HockeySeasonRoster
        fields = ['name', 'season', 'players', 'default']


class HockeySeasonRosterUpdateForm(forms.ModelForm):
    """
    Form for updating a hockey season roster that optimizes db access and excludes any players belonging to different
    teams
    """

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super(HockeySeasonRosterUpdateForm, self).__init__(*args, **kwargs)
        set_fields_disabled(['season'], self.fields)
        if team:
            self.fields['players'].queryset = HockeyPlayer.objects.active().filter(team=team).select_related('user')

    players = forms.ModelMultipleChoiceField(queryset=HockeyPlayer.objects.active().select_related('user'))

    class Meta:
        model = HockeySeasonRoster
        fields = ['name', 'season', 'players', 'default']
