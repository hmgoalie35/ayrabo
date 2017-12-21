from django.contrib import admin

from .models import HockeyPeriod


@admin.register(HockeyPeriod)
class HockeyPeriodAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'game', 'duration', 'complete']
    fields = ['name', 'game', 'duration', 'complete']
    ordering = ['id', 'game']
