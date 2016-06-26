from django.contrib import admin

from .forms import UserProfileAdminForm
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'id', 'roles_mask', 'roles_list_to_string', 'gender', 'birthday', 'height', 'weight', 'language',
        'timezone')
    list_filter = ('user', 'birthday', 'language', 'timezone')
    search_fields = ('user__email',)
    form = UserProfileAdminForm

    def roles_list_to_string(self, obj):
        return ', '.join(obj.roles)

    roles_list_to_string.short_description = 'Roles'


admin.site.register(UserProfile, UserProfileAdmin)
