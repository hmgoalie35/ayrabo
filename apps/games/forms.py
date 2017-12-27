from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from escoresheet.utils.form_fields import SeasonModelChoiceField, TeamModelChoiceField
from games.models import HockeyGame
from seasons.models import Season
from teams.models import Team

DATETIME_INPUT_FORMATS = ['%m/%d/%Y %I:%M %p']


class HockeyGameCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)

        calendar_icon = '<span class="fa fa-calendar"></span>'
        self.helper = FormHelper()
        # csrf token manually included in template
        self.helper.disable_csrf = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div('home_team',
                'away_team',
                'type',
                'point_value',
                'location',
                css_class='col-md-offset-2 col-md-4'),
            Div(PrependedText('start', calendar_icon),
                PrependedText('end', calendar_icon),
                'timezone',
                'season',
                css_class='col-md-4')
        )

        division = self.team.division
        league = division.league
        sport = league.sport

        TeamModel = self.fields['home_team'].queryset.model
        teams = TeamModel.objects.select_related('division').filter(division=division)
        self.fields['home_team'].queryset = teams
        self.fields['away_team'].queryset = teams

        GenericChoiceModel = self.fields['type'].queryset.model
        choices = GenericChoiceModel.objects.get_choices(instance=sport).order_by('long_value')
        self.fields['type'].queryset = choices.filter(type='game_type')
        self.fields['point_value'].queryset = choices.filter(type='game_point_value')

        SeasonModel = self.fields['season'].queryset.model
        self.fields['season'].queryset = SeasonModel.objects.filter(league=league)

        # The current timezone is the same as the timezone on the user's profile.
        self.fields['timezone'].initial = timezone.get_current_timezone_name()

    season = SeasonModelChoiceField(queryset=Season.objects.all())
    home_team = TeamModelChoiceField(queryset=Team.objects.all(), label='Home Team')
    away_team = TeamModelChoiceField(queryset=Team.objects.all(), label='Away Team')
    start = forms.DateTimeField(input_formats=DATETIME_INPUT_FORMATS, label='Game Start')
    end = forms.DateTimeField(input_formats=DATETIME_INPUT_FORMATS, label='Game End')

    class Meta:
        model = HockeyGame
        fields = ['home_team', 'away_team', 'type', 'point_value', 'location', 'start', 'end', 'timezone',
                  'season']
        help_texts = {
            'timezone': 'Please specify the timezone where this game will occur. The default is taken from '
                        'your account.'
        }

    def clean(self):
        cleaned_data = super().clean()
        errors = {}

        home_team = cleaned_data.get('home_team', None)
        away_team = cleaned_data.get('away_team', None)
        if home_team and away_team:
            if home_team.id != self.team.id and away_team.id != self.team.id:
                errors['home_team'] = '{} must be either the home or away team.'.format(self.team.name)
            if home_team.id == away_team.id:
                errors['home_team'] = 'This team must be different than the away team.'
                errors['away_team'] = 'This team must be different than the home team.'

        start = cleaned_data.get('start', None)
        end = cleaned_data.get('end', None)
        if start and end:
            if start >= end:
                errors['end'] = 'Game end must be after game start.'

        if errors:
            raise ValidationError(errors)

        return cleaned_data
