from django.contrib import admin

from .models import League


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'abbreviated_name', 'slug', 'sport']
    list_filter = ['sport']
    search_fields = ['full_name', 'abbreviated_name', 'slug']
    exclude = ['abbreviated_name']
    prepopulated_fields = {'slug': ('full_name',)}
