from django.contrib import admin

from .models import Sport, SportRegistration


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'description')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SportRegistration)
class SportRegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'sport', 'role', 'is_complete', 'created')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'sport__name')
    raw_id_fields = ('user',)
