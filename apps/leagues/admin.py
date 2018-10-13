from django.contrib import admin

from .models import League


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'abbreviated_name', 'slug', 'sport']
    list_filter = ['sport']
    search_fields = ['name', 'abbreviated_name', 'slug']
    exclude = ['abbreviated_name']
    prepopulated_fields = {'slug': ('name',)}
