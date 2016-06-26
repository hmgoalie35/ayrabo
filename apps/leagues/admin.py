from django.contrib import admin
from .models import League


class LeagueAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'abbreviated_name', 'sport']
    list_filter = ['sport']
    search_fields = ['full_name', 'abbreviated_name']
    exclude = ['abbreviated_name']

admin.site.register(League, LeagueAdmin)
