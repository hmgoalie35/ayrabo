from django import forms
from django.contrib import admin
from django.forms import BaseModelFormSet
from django.utils import timezone

from ayrabo.utils.admin.mixins import AdminBulkUploadMixin
from ayrabo.utils.form_fields import SeasonModelChoiceField, TeamModelChoiceField
from common.models import GenericChoice
from games.models import HockeyGame, HockeyGamePlayer
from seasons.models import Season
from sports.models import Sport
from teams.models import Team
from .forms import HockeyGameCreateForm
from .models import HockeyAssist, HockeyGoal


COMMON_FIELDS = ['home_team', 'away_team', 'type', 'point_value', 'status', 'location', 'start', 'end', 'timezone',
                 'season']

COMMON_GAME_FIELDS = ['id', 'home_team', 'away_team', 'start_formatted', 'end_formatted', 'timezone', 'type',
                      'point_value', 'status', 'location', 'season']
PLAYER_SEARCH_FIELDS = ['player__user__first_name', 'player__user__last_name', 'player__jersey_number']


class AbstractGameAdminForm(forms.ModelForm):
    """
    NOTE: This form is solely being used to reduce the number of db queries.
    It lacks validation for home/away teams being different and players belonging to the chosen teams, etc.
    """
    sport_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sport = Sport.objects.get(name=self.sport_name)

        TeamModel = self.fields['home_team'].queryset.model
        teams = TeamModel.objects.select_related('division').filter(division__league__sport=sport)
        self.fields['home_team'].queryset = teams
        self.fields['away_team'].queryset = teams

        GenericChoiceModel = self.fields['type'].queryset.model
        choices = GenericChoiceModel.objects.get_choices(instance=sport)
        self.fields['type'].queryset = choices.filter(type=GenericChoice.GAME_TYPE)
        self.fields['point_value'].queryset = choices.filter(type=GenericChoice.GAME_POINT_VALUE)

        SeasonModel = self.fields['season'].queryset.model
        self.fields['season'].queryset = SeasonModel.objects.select_related('league').filter(league__sport=sport)

        # The current timezone is the same as the timezone on the user's profile.
        self.fields['timezone'].initial = timezone.get_current_timezone_name()

    season = SeasonModelChoiceField(queryset=Season.objects.all())
    home_team = TeamModelChoiceField(queryset=Team.objects.all())
    away_team = TeamModelChoiceField(queryset=Team.objects.all())

    class Meta:
        fields = COMMON_FIELDS


class HockeyGameAdminForm(AbstractGameAdminForm):
    def __init__(self, *args, **kwargs):
        self.sport_name = 'Ice Hockey'
        super().__init__(*args, **kwargs)

    class Meta(AbstractGameAdminForm.Meta):
        model = HockeyGame


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


class AbstractGameAdmin(admin.ModelAdmin):
    list_display = COMMON_GAME_FIELDS
    search_fields = ['home_team__name', 'away_team__name', 'type__long_value', 'location__name']


class HockeyGameAdminModelFormSet(BaseModelFormSet):

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        team_pk = self.data.get(f'form-{index}-team')
        # This can raise a DoesNotExist, there's really no way to have this fail gracefully (via validation errors)
        # We'd need to update the form to not require a team kwarg in the constructor, and have team be a required
        # form field
        team = Team.objects.get(pk=team_pk)
        kwargs.update({'team': team})
        return kwargs


class HockeyGameAdminCreateForm(HockeyGameCreateForm):
    class Meta(HockeyGameCreateForm.Meta):
        fields = HockeyGameCreateForm.Meta.fields + ['team', 'created_by']


@admin.register(HockeyGame)
class HockeyGameAdmin(AdminBulkUploadMixin, AbstractGameAdmin):
    form = HockeyGameAdminForm
    bulk_upload_sample_csv = 'bulk_upload_hockeygames_example.csv'
    bulk_upload_model_form_class = HockeyGameAdminCreateForm
    bulk_upload_model_formset_class = HockeyGameAdminModelFormSet


class AbstractGamePlayerAdmin(admin.ModelAdmin):
    # I want a specific ordering so we'll let subclasses define list display
    list_filter = ('is_starting',)
    # We'll always have fields called game and player for the sport specific subclasses so should be
    # good to include those here
    search_fields = ('team__name', 'player__user__first_name', 'player__user__last_name')
    raw_id_fields = ('team', 'game', 'player')

    def division(self, obj):
        return obj.team.division.name

    def has_add_permission(self, request):
        """
        We aren't checking if the player and team match, team is actually a team for the chosen game, etc.
        We don't want broken records being created so we'll disable adding and changing for now
        """
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(HockeyGamePlayer)
class HockeyGamePlayerAdmin(AbstractGamePlayerAdmin):
    list_display = ('id', 'game_id', 'player', 'team', 'division', 'is_starting', 'created')


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
