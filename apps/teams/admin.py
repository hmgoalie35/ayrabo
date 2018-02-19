from django.contrib import admin

from ayrabo.utils.admin import format_website_link
from locations.models import TeamLocation
from .models import Team


class TeamLocationInline(admin.TabularInline):
    model = TeamLocation


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'slug', 'name', 'division', 'league', 'sport', 'website_link']
    list_display_links = ['name']
    # list_filter = ['division__name', 'division__league__full_name', 'division__league__abbreviated_name',
    #                'division__league__sport__name']
    search_fields = ['name', 'division__name', 'division__league__abbreviated_name', 'division__league__sport__name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [TeamLocationInline]
    exclude = ['locations']

    # README: Do not add in an inline for Season.teams.through. With inlines, there is no way to validate the season's
    # division and the team's division. So a staff member could accidentally add a team for basketball to a season
    # for hockey. The saving in the inline isn't caught by the m2m_changed signal and creating a custom form just for
    # the admin in overkill.

    def website_link(self, obj):
        return format_website_link(obj)

    website_link.short_description = 'Website Link'

    def league(self, obj):
        league = obj.division.league
        return '{full_name} - {abbr_name}'.format(full_name=league.full_name, abbr_name=league.abbreviated_name)

    league.short_description = 'League'

    def sport(self, obj):
        return obj.division.league.sport.name

    sport.short_description = 'Sport'
