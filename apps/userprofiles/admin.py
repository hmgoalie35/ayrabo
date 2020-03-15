from django.contrib import admin

from ayrabo.utils.admin.mixins import AdminBulkUploadMixin
from .forms import UserProfileAdminForm
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(AdminBulkUploadMixin, admin.ModelAdmin):
    list_display = ('id', 'user', 'gender', 'birthday', 'height', 'weight', 'language', 'timezone')
    list_filter = ('gender', 'timezone')
    search_fields = ('user__email',)
    raw_id_fields = ('user',)
    form = UserProfileAdminForm
    bulk_upload_sample_csv = 'bulk_upload_userprofiles_example.csv'
    bulk_upload_model_form_class = UserProfileAdminForm
    bulk_upload_form_fields = ('user', 'gender', 'birthday', 'height', 'weight', 'timezone')
