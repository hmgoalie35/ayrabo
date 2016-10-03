from django.contrib import admin

# from .forms import SeasonAdminForm, HockeySeasonRosterAdminForm
from .models import Season, HockeySeasonRoster


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['id', 'season', 'start_date', 'end_date', 'league', 'sport']
    list_display_links = ['season']
    search_fields = ['id', 'start_date', 'end_date']
    filter_horizontal = ['teams']
    # form = SeasonAdminForm

    def season(self, obj):
        return str(obj)

    season.short_description = 'Season'

    def sport(self, obj):
        return obj.league.sport

    sport.short_description = 'Sport'


@admin.register(HockeySeasonRoster)
class HockeySeasonRosterAdmin(admin.ModelAdmin):
    list_display = ['id', 'season', 'team', 'division', 'default', 'created']
    list_display_links = ['season']
    search_fields = ['team__name', 'season__start_date', 'season__end_date']
    filter_horizontal = ['players']
    # form = HockeySeasonRosterAdminForm

    def division(self, obj):
        return obj.team.division

    division.short_description = 'Division'
