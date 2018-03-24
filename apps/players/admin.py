from django.contrib import admin

from . import models


@admin.register(models.HockeyPlayer)
class HockeyPlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'position', 'handedness', 'jersey_number', 'team', 'division', 'league', 'sport',
                    'is_active']
    search_fields = ['id', 'user__email', 'user__first_name', 'user__last_name', 'jersey_number', 'team__name']


@admin.register(models.BaseballPlayer)
class BaseballPlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'position', 'catches', 'bats', 'jersey_number', 'team', 'division', 'league', 'sport',
                    'is_active']
    search_fields = ['id', 'user__email', 'user__first_name', 'user__last_name', 'jersey_number', 'team__name']


@admin.register(models.BasketballPlayer)
class BasketballPlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'team', 'position', 'shoots', 'jersey_number', 'team', 'division', 'league', 'sport',
                    'is_active']
    search_fields = ['id', 'user__email', 'user__first_name', 'user__last_name', 'jersey_number', 'team__name']
