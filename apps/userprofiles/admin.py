from django.contrib import admin

from .forms import UserProfileAdminForm, RolesMaskAdminForm
from .models import UserProfile, RolesMask


class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'roles_mask', 'roles_list_to_string', 'gender', 'birthday', 'height', 'weight',
        'language',
        'timezone']
    list_display_links = ['user']
    list_filter = ['roles_mask']
    search_fields = ['user__email']
    form = UserProfileAdminForm
    readonly_fields = ['roles_mask']

    def roles_list_to_string(self, obj):
        return ', '.join(obj.roles)

    roles_list_to_string.short_description = 'Roles'

    def get_form(self, request, obj=None, **kwargs):
        form = super(UserProfileAdmin, self).get_form(request, obj, **kwargs)
        if obj is not None:
            form.declared_fields['roles'].initial = obj.roles
        return form

    def save_model(self, request, obj, form, change):
        obj.set_roles(form.cleaned_data['roles'])


class RolesMaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'roles_mask', 'roles_mask_to_string', 'are_role_objects_created', 'are_roles_set', 'sport']
    list_display_links = ['user']
    form = RolesMaskAdminForm
    readonly_fields = ['roles_mask']

    def roles_mask_to_string(self, obj):
        return ', '.join(obj.roles)

    roles_mask_to_string.short_description = 'Roles'

    def get_form(self, request, obj=None, **kwargs):
        form = super(RolesMaskAdmin, self).get_form(request, obj, **kwargs)
        if obj is not None:
            form.declared_fields['roles'].initial = obj.roles
        return form

    def save_model(self, request, obj, form, change):
        obj.set_roles(form.cleaned_data['roles'])


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(RolesMask, RolesMaskAdmin)
