from django.contrib import admin

from escoresheet.utils.admin import format_website_link
from locations.models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'street_number', 'street', 'city', 'state', 'zip_code', 'phone_number',
                    'website_link', 'created']
    list_display_links = ['name']
    search_fields = ['id', 'name', 'street', 'street_number', 'city', 'state', 'zip_code']
    list_filter = ['city', 'state']

    prepopulated_fields = {'slug': ('name',)}

    def website_link(self, obj):
        return format_website_link(obj)

    website_link.short_description = 'Website Link'
