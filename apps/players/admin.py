from django import forms
from django.contrib import admin

from ayrabo.utils.admin.mixins import AdminBulkUploadMixin
from sports.models import Sport, SportRegistration
from . import models


class PlayerAdminModelFormSet(forms.BaseModelFormSet):
    def save(self, commit=True):
        instances = super().save(commit=commit)
        for instance in instances:
            SportRegistration.objects.get_or_create(
                user=instance.user,
                sport=instance.sport,
                role=SportRegistration.PLAYER,
                defaults={'is_complete': True},
            )
        return instances


class HockeyPlayerAdminForm(forms.ModelForm):
    sport = forms.ModelChoiceField(queryset=Sport.objects.all(), required=False)

    def clean(self):
        super().clean()
        team = self.cleaned_data.get('team')
        self.cleaned_data.update({'sport': team.division.league.sport})
        return self.cleaned_data

    class Meta:
        model = models.HockeyPlayer
        fields = ('user', 'sport', 'team', 'jersey_number', 'position', 'handedness')


@admin.register(models.HockeyPlayer)
class HockeyPlayerAdmin(AdminBulkUploadMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'position',
        'handedness',
        'jersey_number',
        'team',
        'division',
        'league',
        'sport',
        'is_active'
    )
    search_fields = ('id', 'user__email', 'user__first_name', 'user__last_name', 'jersey_number', 'team__name')
    bulk_upload_sample_csv = 'bulk_upload_hockeyplayers_example.csv'
    bulk_upload_form_fields = ('user', 'sport', 'team', 'jersey_number', 'position', 'handedness')
    bulk_upload_model_formset_class = PlayerAdminModelFormSet
    bulk_upload_model_form_class = HockeyPlayerAdminForm


@admin.register(models.BaseballPlayer)
class BaseballPlayerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'position',
        'catches',
        'bats',
        'jersey_number',
        'team',
        'division',
        'league',
        'sport',
        'is_active'
    )
    search_fields = ('id', 'user__email', 'user__first_name', 'user__last_name', 'jersey_number', 'team__name')


@admin.register(models.BasketballPlayer)
class BasketballPlayerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'team',
        'position',
        'shoots',
        'jersey_number',
        'team',
        'division',
        'league',
        'sport',
        'is_active'
    )
    search_fields = ('id', 'user__email', 'user__first_name', 'user__last_name', 'jersey_number', 'team__name')
