from django.contrib import admin
from django import forms

from ayrabo.utils.admin.mixins import AdminBulkUploadMixin
from sports.models import SportRegistration
from .models import Coach


class CoachAdminModelFormSet(forms.BaseModelFormSet):
    def save(self, commit=True):
        instances = super().save(commit=commit)
        for instance in instances:
            SportRegistration.objects.get_or_create(
                user=instance.user,
                sport=instance.team.division.league.sport,
                role=SportRegistration.COACH,
                defaults={'is_complete': True},
            )
        return instances


@admin.register(Coach)
class CoachAdmin(AdminBulkUploadMixin, admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'position', 'team', 'division', 'league', 'sport', 'is_active']
    search_fields = ['user__email', 'position']
    bulk_upload_sample_csv = 'bulk_upload_coaches_example.csv'
    bulk_upload_form_fields = ('user', 'position', 'team', 'is_active')
    bulk_upload_model_formset_class = CoachAdminModelFormSet

    def name(self, obj):
        return str(obj)

    name.short_description = 'Name'

    def division(self, obj):
        return obj.team.division.name

    division.short_description = 'Division'

    def league(self, obj):
        return obj.team.division.league.name

    league.short_description = 'League'

    def sport(self, obj):
        return obj.team.division.league.sport

    sport.short_description = 'Sport'
