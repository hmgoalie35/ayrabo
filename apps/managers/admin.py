from django.contrib import admin
from django import forms

from ayrabo.utils.admin.mixins import AdminBulkUploadMixin
from sports.models import SportRegistration
from . import models


class ManagerAdminModelFormSet(forms.BaseModelFormSet):
    def save(self, commit=True):
        instances = super().save(commit=commit)
        for instance in instances:
            SportRegistration.objects.get_or_create(
                user=instance.user,
                sport=instance.team.division.league.sport,
                role=SportRegistration.MANAGER,
                defaults={'is_complete': True},
            )
        return instances


@admin.register(models.Manager)
class ManagerAdmin(AdminBulkUploadMixin, admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'team', 'division', 'league', 'sport', 'is_active']
    search_fields = ['user__email', 'team__name']
    bulk_upload_sample_csv = 'bulk_upload_managers_example.csv'
    bulk_upload_form_fields = ('user', 'team', 'is_active')
    bulk_upload_model_formset_class = ManagerAdminModelFormSet

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
