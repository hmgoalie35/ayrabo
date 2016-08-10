from django.contrib import admin

from .models import Division


class DivisionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'league']
    list_display_links = ['name']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Division, DivisionAdmin)
