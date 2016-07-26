from django.contrib import admin

from .models import HockeyPlayer


class HockeyPlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'team', 'position', 'handedness', 'jersey_number', 'created']
    list_display_links = ['user']


admin.site.register(HockeyPlayer, HockeyPlayerAdmin)
