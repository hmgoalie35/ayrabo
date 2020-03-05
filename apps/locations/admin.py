from django.contrib import admin

from ayrabo.utils.admin import format_website_link
from ayrabo.utils.admin.mixins import AdminBulkUploadMixin
from locations.models import Location


@admin.register(Location)
class LocationAdmin(AdminBulkUploadMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
        'street_number',
        'street',
        'city',
        'state',
        'zip_code',
        'phone_number',
        'website_link',
        'created'
    )
    search_fields = ('id', 'name', 'street', 'street_number', 'city', 'state', 'zip_code')
    list_filter = ('city', 'state')
    prepopulated_fields = {'slug': ('name',)}
    bulk_upload_sample_csv = 'bulk_upload_locations_example.csv'
    bulk_upload_form_fields = (
        'name',
        'street',
        'street_number',
        'city',
        'state',
        'zip_code',
        'phone_number',
        'website'
    )

    def website_link(self, obj):
        return format_website_link(obj)

    website_link.short_description = 'Website Link'
