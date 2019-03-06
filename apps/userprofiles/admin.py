from django.contrib import admin

from .forms import UserProfileAdminForm
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'gender', 'birthday', 'height', 'weight', 'language', 'timezone')
    list_filter = ('gender', 'timezone')
    search_fields = ('user__email',)
    raw_id_fields = ('user',)
    form = UserProfileAdminForm
