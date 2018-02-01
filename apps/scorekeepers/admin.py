from django.contrib import admin

from scorekeepers.models import Scorekeeper


@admin.register(Scorekeeper)
class ScorekeeperAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'sport', 'is_active', 'created']
    list_display_links = ['user']
    search_fields = ['user__email', 'sport__name']
    raw_id_fields = ['user']
