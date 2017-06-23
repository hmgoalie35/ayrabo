from django.contrib import admin

from .models import Referee


@admin.register(Referee)
class RefereeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'league', 'sport', 'is_active']
    list_display_links = ['name']
    search_fields = ['user__email', 'league__full_name']

    def name(self, obj):
        return str(obj)

    name.short_description = 'Name'

    def sport(self, obj):
        return obj.league.sport

    sport.short_description = 'Sport'
