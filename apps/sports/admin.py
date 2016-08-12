from django.contrib import admin

from . import models, forms


@admin.register(models.Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'description')
    list_display_links = ['name']
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(models.SportRegistration)
class SportRegistrationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'roles_mask', 'roles_mask_to_string', 'is_complete', 'sport']
    list_display_links = ['user']
    form = forms.SportRegistrationAdminForm
    readonly_fields = ['roles_mask']

    def roles_mask_to_string(self, obj):
        return ', '.join(obj.roles)

    roles_mask_to_string.short_description = 'Roles'

    def get_form(self, request, obj=None, **kwargs):
        form = super(SportRegistrationAdmin, self).get_form(request, obj, **kwargs)
        if obj is not None:
            form.declared_fields['roles'].initial = obj.roles
        return form

    def save_model(self, request, obj, form, change):
        obj.set_roles(form.cleaned_data['roles'])
