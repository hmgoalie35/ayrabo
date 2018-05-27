from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Permission, User

admin.site.register(User, UserAdmin)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'content_type', 'object_id', 'content_object')
    raw_id_fields = ('user',)
    search_fields = ('user__email', 'name')
