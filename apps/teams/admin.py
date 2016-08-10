from django.contrib import admin
from django.utils.html import format_html

from .models import Team


class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'division', 'league', 'sport', 'website_link']
    list_display_links = ['name']
    # list_filter = ['division__name', 'division__league__full_name', 'division__league__abbreviated_name',
    #                'division__league__sport__name']
    search_fields = ['name', 'division__name', 'division__league__abbreviated_name', 'division__league__sport__name']
    prepopulated_fields = {'slug': ('name',)}

    def website_link(self, obj):
        return format_html('<a target="_blank" href="{url}">{url}</a>', url=obj.website)

    website_link.short_description = 'Website Link'

    def league(self, obj):
        league = obj.division.league
        return '{full_name} - {abbr_name}'.format(full_name=league.full_name, abbr_name=league.abbreviated_name)

    league.short_description = 'League'

    def sport(self, obj):
        return obj.division.league.sport.name

    sport.short_description = 'Sport'


admin.site.register(Team, TeamAdmin)
