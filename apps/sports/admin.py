from django.contrib import admin
from .models import Sport


class SportAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name', )}


admin.site.register(Sport, SportAdmin)
