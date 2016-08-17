from django.contrib import admin

from .forms import SeasonAdminForm
from .models import Season


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['id', 'season', 'start_date', 'end_date', 'division', 'league', 'sport']
    list_display_links = ['season']
    search_fields = ['id', 'start_date', 'end_date']
    filter_horizontal = ['teams']
    form = SeasonAdminForm

    def season(self, obj):
        return str(obj)

    season.short_description = 'Season'

    def league(self, obj):
        return obj.division.league

    league.short_description = 'League'

    def sport(self, obj):
        return obj.division.league.sport

    sport.short_description = 'Sport'
