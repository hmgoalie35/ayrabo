from django.contrib import admin

from .models import Coach


class CoachAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'team', 'league', 'position']
    list_display_links = ['name']
    search_fields = ['user__email', 'position']

    def name(self, obj):
        return str(obj)

    name.short_description = 'Name'

    def league(self, obj):
        return obj.team.division.league.full_name

    league.short_description = 'League'


admin.site.register(Coach, CoachAdmin)
