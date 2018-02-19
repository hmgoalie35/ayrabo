from django.contrib import admin

from common.models import GenericChoice


@admin.register(GenericChoice)
class GenericChoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'short_value', 'long_value', 'type', 'content_object', 'content_type', 'object_id']
    search_fields = ['short_value', 'long_value']
