from django.contrib import admin

from .models import Referee


class RefereeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'division', 'league', 'sport']
    list_display_links = ['name']
    search_fields = ['user__email', 'division__name']

    def name(self, obj):
        return str(obj)

    name.short_description = 'Name'

    def league(self, obj):
        return obj.division.league.full_name

    league.short_description = 'League'

    def sport(self, obj):
        return obj.division.league.sport

    sport.short_description = 'Sport'

admin.site.register(Referee, RefereeAdmin)
