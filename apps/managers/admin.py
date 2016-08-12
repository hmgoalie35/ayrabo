from django.contrib import admin

from .models import Manager


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'team', 'division', 'league', 'sport']
    list_display_links = ['name']
    search_fields = ['user__email', 'team__name']

    def name(self, obj):
        return str(obj)

    name.short_description = 'Name'

    def division(self, obj):
        return obj.team.division.name

    division.short_description = 'Division'

    def league(self, obj):
        return obj.team.division.league.full_name

    league.short_description = 'League'

    def sport(self, obj):
        return obj.team.division.league.sport

    sport.short_description = 'Sport'
