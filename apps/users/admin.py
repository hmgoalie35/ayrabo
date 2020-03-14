from allauth.account.models import EmailAddress
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.forms import BaseModelFormSet

from ayrabo.utils.admin.mixins import AdminBulkUploadMixin
from .models import Permission, User


class UserAdminForm(forms.ModelForm):
    # max_length taken from AbstractBaseUser
    username = forms.CharField(max_length=150, required=False)

    def clean(self):
        super().clean()
        email = self.cleaned_data.get('email')
        self.cleaned_data.update({'username': email})

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class UserAdminModelFormSet(BaseModelFormSet):
    def save(self, commit=True):
        instances = super().save(commit=commit)
        for user in instances:
            email_address = EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=False
            )
            email_address.send_confirmation()
        return instances


@admin.register(User)
class UserAdmin(AdminBulkUploadMixin, BaseUserAdmin):
    bulk_upload_sample_csv = 'bulk_upload_users_example.csv'
    bulk_upload_model_form_class = UserAdminForm
    bulk_upload_model_formset_class = UserAdminModelFormSet


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'content_type', 'object_id', 'content_object')
    raw_id_fields = ('user',)
    search_fields = ('user__email', 'name')
