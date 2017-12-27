from django import forms
from django.contrib import admin
from django.utils import timezone

from escoresheet.utils.form_fields import SeasonModelChoiceField, TeamModelChoiceField
from games.models import HockeyGame
from seasons.models import Season
from sports.models import Sport
from teams.models import Team
from .models import HockeyGoal, HockeyAssist

COMMON_FIELDS = ['home_team', 'away_team', 'type', 'point_value', 'status', 'location', 'start', 'end', 'timezone',
                 'season']

COMMON_GAME_FIELDS = ['id', 'home_team', 'away_team', 'start_formatted', 'end_formatted', 'timezone', 'type',
                      'point_value', 'status', 'location', 'season']
PLAYER_SEARCH_FIELDS = ['player__user__first_name', 'player__user__last_name', 'player__jersey_number']


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


@admin.register(HockeyGame)
class HockeyGameAdmin(admin.ModelAdmin):
    list_display = COMMON_GAME_FIELDS
    search_fields = ['home_team__name', 'away_team__name', 'type__long_value', 'location__name']
    filter_horizontal = ['home_players', 'away_players']
    form = HockeyGameAdminForm

    def start_formatted(self, obj):
        return obj.datetime_formatted(obj.start)

    start_formatted.short_description = 'Start'

    def end_formatted(self, obj):
        return obj.datetime_formatted(obj.end)

    end_formatted.short_description = 'End'


@admin.register(HockeyGoal)
class HockeyGoalAdmin(admin.ModelAdmin):
    list_display = ['id', 'game', 'period', 'time', 'player', 'type', 'penalty', 'empty_net', 'value']
    search_fields = ['type'] + PLAYER_SEARCH_FIELDS
    form = HockeyGoalAdminForm


@admin.register(HockeyAssist)
class HockeyAssistAdmin(admin.ModelAdmin):
    list_display = ['id', 'player', 'goal']
    raw_id_fields = ['goal']
    search_fields = PLAYER_SEARCH_FIELDS + ['goal__player__user__first_name', 'goal__player__user__last_name']
    form = HockeyAssistAdminForm
