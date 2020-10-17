from django.contrib import admin
from django import forms

from ayrabo.utils.admin.mixins import AdminBulkUploadMixin
from sports.models import SportRegistration
from .models import Referee


class RefereeAdminModelFormSet(forms.BaseModelFormSet):
    def save(self, commit=True):
        instances = super().save(commit=commit)
        for instance in instances:
            SportRegistration.objects.get_or_create(
                user=instance.user,
                sport=instance.league.sport,
                role=SportRegistration.REFEREE,
                defaults={'is_complete': True},
            )
        return instances


@admin.register(Referee)
class RefereeAdmin(AdminBulkUploadMixin, admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'league', 'sport', 'is_active']
    search_fields = ['user__email', 'league__name']
    bulk_upload_sample_csv = 'bulk_upload_referees_example.csv'
    bulk_upload_form_fields = ('user', 'league', 'is_active')
    bulk_upload_model_formset_class = RefereeAdminModelFormSet

    def name(self, obj):
        return str(obj)

    name.short_description = 'Name'

    def sport(self, obj):
        return obj.league.sport

    sport.short_description = 'Sport'
