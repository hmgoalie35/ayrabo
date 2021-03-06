from django.contrib import admin
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.widgets import ImageClearableFileInput

from ayrabo.utils.admin import format_website_link
from ayrabo.utils.admin.mixins import AdminBulkUploadMixin
from locations.models import TeamLocation
from .models import Team


class TeamLocationInline(admin.TabularInline):
    model = TeamLocation


@admin.register(Team)
class TeamAdmin(AdminBulkUploadMixin, admin.ModelAdmin):
    list_display = ['id', 'slug', 'name', 'get_logo', 'organization', 'division', 'league', 'sport', 'website_link']
    search_fields = ['name', 'division__name', 'division__league__abbreviated_name', 'division__league__sport__name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [TeamLocationInline]
    exclude = ['locations']
    formfield_overrides = {
        ThumbnailerImageField: {'widget': ImageClearableFileInput},
    }
    bulk_upload_sample_csv = 'bulk_upload_teams_example.csv'
    bulk_upload_form_fields = ('name', 'website', 'division', 'organization')

    # WARNING: Do not add in an inline for Season.teams.through. With inlines, there is no way to validate the season's
    # division and the team's division. A staff member could accidentally add a team for basketball to a season
    # for hockey. The saving in the inline isn't caught by the m2m_changed signal and creating a custom form just for
    # the admin is overkill.

    def website_link(self, obj):
        return format_website_link(obj)

    website_link.short_description = 'Website Link'

    def league(self, obj):
        league = obj.division.league
        return '{} - {}'.format(league.name, league.abbreviated_name)

    league.short_description = 'League'

    def sport(self, obj):
        return obj.division.league.sport.name

    sport.short_description = 'Sport'

    def get_logo(self, obj):
        return bool(obj.logo)

    get_logo.short_description = 'Logo'
    get_logo.boolean = True
