from django.contrib import admin

from .models import League


class LeagueAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'abbreviated_name', 'slug', 'sport']
    list_display_links = ['full_name']
    list_filter = ['sport']
    search_fields = ['full_name', 'abbreviated_name', 'slug']
    exclude = ['abbreviated_name']
    prepopulated_fields = {'slug': ('full_name',)}


admin.site.register(League, LeagueAdmin)
