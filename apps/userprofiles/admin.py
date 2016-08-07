from django.contrib import admin

from .forms import UserProfileAdminForm
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'gender', 'birthday', 'height', 'weight',
        'language',
        'timezone']
    list_display_links = ['user']
    search_fields = ['user__email']
    form = UserProfileAdminForm


admin.site.register(UserProfile, UserProfileAdmin)
