from django.contrib import admin

from games.forms import HockeyGameAdminForm, HockeyGoalAdminForm, HockeyAssistAdminForm
from .models import HockeyGame, HockeyGoal, HockeyAssist


COMMON_GAME_FIELDS = ['id', 'home_team', 'away_team', 'start', 'end', 'timezone', 'type', 'point_value', 'status',
                      'location',
                      'season']
PLAYER_SEARCH_FIELDS = ['player__user__first_name', 'player__user__last_name', 'player__jersey_number']


@admin.register(HockeyGame)
class HockeyGameAdmin(admin.ModelAdmin):
    list_display = COMMON_GAME_FIELDS
    search_fields = ['home_team__name', 'away_team__name', 'type__long_value', 'location__name']
    filter_horizontal = ['home_players', 'away_players']
    form = HockeyGameAdminForm


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
