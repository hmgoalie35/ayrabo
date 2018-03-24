from django.contrib import admin

from .forms import SeasonAdminForm, HockeySeasonRosterAdminForm
from .models import Season, HockeySeasonRoster


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['id', 'season', 'start_date', 'end_date', 'league', 'sport', 'expired']
    search_fields = ['id', 'start_date', 'end_date']
    filter_horizontal = ['teams']
    form = SeasonAdminForm

    def season(self, obj):
        return str(obj)

    def expired(self, obj):
        return obj.expired

    expired.boolean = True

    season.short_description = 'Season'

    def sport(self, obj):
        return obj.league.sport

    sport.short_description = 'Sport'


@admin.register(HockeySeasonRoster)
class HockeySeasonRosterAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'season', 'team', 'division', 'default', 'expired', 'created_by', 'created']
    search_fields = ['team__name', 'season__start_date', 'season__end_date']
    filter_horizontal = ['players']
    readonly_fields = ['created_by']
    form = HockeySeasonRosterAdminForm

    def save_model(self, request, obj, form, change):
        if obj.created_by is None:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def division(self, obj):
        return obj.team.division

    def expired(self, obj):
        return obj.season.expired

    expired.boolean = True

    division.short_description = 'Division'
