from allauth.account.models import EmailAddress
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.sites.shortcuts import get_current_site
from django.forms import BaseModelFormSet

from ayrabo.utils.admin.mixins import AdminBulkUploadMixin
from ayrabo.utils.email import send_mail
from ayrabo.utils.urls import get_absolute_url
from .models import Permission, User


class UserAdminForm(forms.ModelForm):
    # max_length taken from AbstractBaseUser
    username = forms.CharField(max_length=150, required=False)
    # Email is not required by default when creating a user, we want it required
    email = forms.EmailField()

    def clean(self):
        super().clean()
        email = self.cleaned_data.get('email')
        self.cleaned_data.update({'username': email})
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class UserAdminModelFormSet(BaseModelFormSet):
    def save(self, commit=True):
        instances = super().save(commit=commit)
        for user in instances:
            user.set_unusable_password()
            user.save()

            email_address = EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=False
            )

            site = get_current_site(request=None)
            # We want this informative welcome email to be sent first. It's possible the user doesn't actually receive
            # this email first but at least we tried.
            send_mail(
                subject=f'Welcome to {site.name}!',
                recipient_list=[user.email],
                message='admin/emails/bulk_uploaded_users_welcome.txt',
                html_message='admin/emails/bulk_uploaded_users_welcome.html',
                context={
                    'user': user,
                    'site': site,
                    'confirm_email_url': get_absolute_url('account_confirm_email', 'new-confirmation-link'),
                    'password_reset_url': get_absolute_url('account_reset_password'),
                }
            )
            email_address.send_confirmation()
        return instances


@admin.register(User)
class UserAdmin(AdminBulkUploadMixin, BaseUserAdmin):
    list_display = ('id',) + BaseUserAdmin.list_display
    bulk_upload_sample_csv = 'bulk_upload_users_example.csv'
    bulk_upload_model_form_class = UserAdminForm
    bulk_upload_model_formset_class = UserAdminModelFormSet


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'content_type', 'object_id', 'content_object')
    raw_id_fields = ('user',)
    search_fields = ('user__email', 'name')
