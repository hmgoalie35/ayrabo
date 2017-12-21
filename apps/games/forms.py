from django import forms
from django.utils import timezone

from escoresheet.utils.form_fields import SeasonModelChoiceField, TeamModelChoiceField
from games.models import HockeyGame
from seasons.models import Season
from sports.models import Sport
from teams.models import Team


COMMON_FIELDS = ['home_team', 'away_team', 'type', 'point_value', 'status', 'location', 'start', 'end', 'timezone',
                 'season']


class HockeyGameAdminForm(forms.ModelForm):
    """
    NOTE: This form is currently being used to just reduce the number of db queries. It is lacking the necessary
    validation for home/away teams being different and players belonging to the chosen teams, etc.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sport = Sport.objects.get(name='Ice Hockey')

        TeamModel = self.fields['home_team'].queryset.model
        teams = TeamModel.objects.select_related('division').filter(division__league__sport=sport)
        self.fields['home_team'].queryset = teams
        self.fields['away_team'].queryset = teams

        HockeyPlayerModel = self.fields['home_players'].queryset.model
        players = HockeyPlayerModel.objects.active().select_related('user').filter(sport=sport)
        self.fields['home_players'].queryset = players
        self.fields['away_players'].queryset = players

        GenericChoiceModel = self.fields['type'].queryset.model
        choices = GenericChoiceModel.objects.get_choices(instance=sport)
        self.fields['type'].queryset = choices.filter(type='game_type')
        self.fields['point_value'].queryset = choices.filter(type='game_point_value')

        SeasonModel = self.fields['season'].queryset.model
        self.fields['season'].queryset = SeasonModel.objects.filter(league__sport=sport).select_related('league')

        # The current timezone is the same as the timezone on the user's profile.
        self.fields['timezone'].initial = timezone.get_current_timezone_name()

    season = SeasonModelChoiceField(queryset=Season.objects.all())
    home_team = TeamModelChoiceField(queryset=Team.objects.all())
    away_team = TeamModelChoiceField(queryset=Team.objects.all())

    class Meta:
        model = HockeyGame
        fields = COMMON_FIELDS + ['home_players', 'away_players']


class HockeyGoalAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sport = Sport.objects.get(name='Ice Hockey')

        HockeyPlayerModel = self.fields['player'].queryset.model
        players = HockeyPlayerModel.objects.active().select_related('user').filter(sport=sport)
        self.fields['player'].queryset = players


class HockeyAssistAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sport = Sport.objects.get(name='Ice Hockey')

        HockeyPlayerModel = self.fields['player'].queryset.model
        players = HockeyPlayerModel.objects.active().select_related('user').filter(sport=sport)
        self.fields['player'].queryset = players
