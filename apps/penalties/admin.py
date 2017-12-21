from django.contrib import admin

from penalties.forms import HockeyPenaltyAdminForm
from .models import HockeyPenalty, GenericPenaltyChoice


@admin.register(HockeyPenalty)
class HockeyPenaltyAdmin(admin.ModelAdmin):
    list_display = ['id', 'game', 'period', 'type', 'duration', 'player', 'time_in', 'time_out']
    search_fields = ['player__user__first_name', 'player__user__last_name']
    form = HockeyPenaltyAdminForm


@admin.register(GenericPenaltyChoice)
class GenericPenaltyChoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'content_object', 'content_type', 'object_id']
    search_fields = ['name']
    ordering = ['name', 'content_type']
