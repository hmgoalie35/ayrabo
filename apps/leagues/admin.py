from django.contrib import admin
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.widgets import ImageClearableFileInput

from ayrabo.utils.admin import format_website_link
from .models import League


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'get_logo', 'abbreviated_name', 'slug', 'sport', 'website_link']
    list_filter = ['sport']
    search_fields = ['name', 'abbreviated_name', 'slug']
    exclude = ['abbreviated_name']
    prepopulated_fields = {'slug': ('name',)}
    formfield_overrides = {
        ThumbnailerImageField: {'widget': ImageClearableFileInput},
    }

    def get_logo(self, obj):
        return bool(obj.logo)

    get_logo.short_description = 'Logo'
    get_logo.boolean = True

    def website_link(self, obj):
        return format_website_link(obj)

    website_link.short_description = 'Website Link'
