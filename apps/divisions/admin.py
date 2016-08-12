from django.contrib import admin

from .models import Division


class DivisionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'league', 'sport']
    list_display_links = ['name']
    search_fields = ['name', 'slug', 'league__full_name']
    prepopulated_fields = {'slug': ('name',)}

    def sport(self, obj):
        return obj.league.sport

    sport.short_description = 'Sport'


admin.site.register(Division, DivisionAdmin)
