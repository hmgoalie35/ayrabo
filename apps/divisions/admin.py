from django.contrib import admin
from .models import Division


class DivisionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'league']
    search_fields = ['name']


admin.site.register(Division, DivisionAdmin)
