from django.contrib import admin

from . import models


class HockeyPlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'team', 'position', 'handedness', 'jersey_number', 'created']
    list_display_links = ['user']


class BaseballPlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'team', 'position', 'catches', 'bats', 'jersey_number', 'created']
    list_display_links = ['user']


class BasketballPlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'team', 'position', 'shoots', 'jersey_number', 'created']
    list_display_links = ['user']


admin.site.register(models.HockeyPlayer, HockeyPlayerAdmin)
admin.site.register(models.BaseballPlayer, BaseballPlayerAdmin)
admin.site.register(models.BasketballPlayer, BasketballPlayerAdmin)
