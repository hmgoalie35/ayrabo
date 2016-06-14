from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'gender', 'birthday', 'height', 'weight', 'language', 'timezone')
    list_filter = ('user', 'birthday', 'language', 'timezone')
    search_fields = ('user__email', )

admin.site.register(UserProfile, UserProfileAdmin)
