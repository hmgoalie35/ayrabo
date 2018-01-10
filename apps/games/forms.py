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


class AbstractGameCreateForm(forms.ModelForm):
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
        self.fields['season'].queryset = SeasonModel.objects.select_related('league').filter(league=league)

        # The current timezone is the same as the timezone on the user's profile.
        self.fields['timezone'].initial = timezone.get_current_timezone_name()

    season = SeasonModelChoiceField(queryset=Season.objects.all())
    home_team = TeamModelChoiceField(queryset=Team.objects.all(), label='Home Team')
    away_team = TeamModelChoiceField(queryset=Team.objects.all(), label='Away Team')
    start = forms.DateTimeField(input_formats=DATETIME_INPUT_FORMATS, label='Game Start')
    end = forms.DateTimeField(input_formats=DATETIME_INPUT_FORMATS, label='Game End')

    class Meta:
        fields = ['home_team', 'away_team', 'type', 'point_value', 'location', 'start', 'end', 'timezone', 'season']
        help_texts = {
            'timezone': 'Please specify the timezone where this game will occur. The default is taken from '
                        'your account.'
        }

    def clean(self):
        cleaned_data = super().clean()
        field_errors = {}

        home_team = cleaned_data.get('home_team', None)
        away_team = cleaned_data.get('away_team', None)
        if home_team and away_team:
            if home_team.id != self.team.id and away_team.id != self.team.id:
                field_errors['home_team'] = '{} must be either the home or away team.'.format(self.team.name)
            if home_team.id == away_team.id:
                field_errors['home_team'] = 'This team must be different than the away team.'
                field_errors['away_team'] = 'This team must be different than the home team.'

        start = cleaned_data.get('start', None)
        end = cleaned_data.get('end', None)
        if start and end:
            if start >= end:
                field_errors['end'] = 'Game end must be after game start.'

        season = cleaned_data.get('season', None)
        if start and end and season:
            game_start = start.date()
            game_end = end.date()
            season_start = season.start_date
            season_end = season.end_date
            DATE_FORMAT = '%m/%d/%Y'
            date_out_of_bounds_error_msg = 'This date does not occur during the {}-{} season ({}-{}).'.format(
                season_start.year,
                season_end.year,
                season_start.strftime(DATE_FORMAT),
                season_end.strftime(DATE_FORMAT))

            # NOTE These validation errors overwrite previous start/end validation errors (which is expected).
            # The error messages below are more informative.

            # Games on the season start/end date are considered valid.
            if not (season_start <= game_start <= season_end):
                field_errors['start'] = date_out_of_bounds_error_msg
            if not (season_start <= game_end <= season_end):
                field_errors['end'] = date_out_of_bounds_error_msg

        tz = cleaned_data.get('timezone', None)
        if all([home_team, away_team, start, tz]):
            qs = self.Meta.model.objects.filter(start=start, timezone=tz)
            team_error_msg = 'This team already has a game for the selected game start and timezone.'
            if qs.filter(home_team=home_team).exists():
                field_errors['home_team'] = team_error_msg
                # Forces the fields to be rendered in the error state.
                field_errors['start'] = ''
                field_errors['timezone'] = ''
            if qs.filter(away_team=away_team).exists():
                field_errors['away_team'] = team_error_msg
                field_errors['start'] = ''
                field_errors['timezone'] = ''

        if field_errors:
            raise ValidationError(field_errors)

        return cleaned_data


class HockeyGameCreateForm(AbstractGameCreateForm):
    class Meta(AbstractGameCreateForm.Meta):
        model = HockeyGame
