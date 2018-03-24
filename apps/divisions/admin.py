from django.contrib import admin

from .models import Division


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'league', 'sport']
    search_fields = ['name', 'slug', 'league__full_name']
    prepopulated_fields = {'slug': ('name',)}

    def sport(self, obj):
        return obj.league.sport

    sport.short_description = 'Sport'
