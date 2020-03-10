from django.contrib import messages
from django.shortcuts import redirect
from django.templatetags.static import static
from django.urls import path, reverse_lazy
from django_object_actions import DjangoObjectActions

from ayrabo.utils.admin.views import AdminBulkUploadView


class AdminBulkUploadMixin(DjangoObjectActions):
    bulk_upload_sample_csv = None
    bulk_upload_form_fields = None
    bulk_upload_model_form_class = None
    bulk_upload_model_formset_class = None
    bulk_upload_view_class = AdminBulkUploadView
    changelist_actions = ('bulk_upload', 'download_sample_bulk_upload_csv')

    def get_url_name(self):
        _meta = self.model._meta
        return f'{_meta.app_label}_{_meta.model_name}_bulk_upload'

    def bulk_upload_view(self):
        _meta = self.model._meta
        return self.bulk_upload_view_class.as_view(
            success_url=reverse_lazy(f'admin:{_meta.app_label}_{_meta.model_name}_changelist'),
            model=self.model,
            model_form_class=self.bulk_upload_model_form_class,
            model_formset_class=self.bulk_upload_model_formset_class,
            fields=self.bulk_upload_form_fields,
            admin_site=self.admin_site,
            extra_context={
                'title': f'Bulk upload {_meta.verbose_name_plural}',
                'opts': _meta,  # Django's base admin template expects this variable in the context
            }
        )

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload_view()), name=self.get_url_name())
        ]
        return new_urls + urls

    def bulk_upload(self, *args, **kwargs):
        return redirect(f'admin:{self.get_url_name()}')

    def download_sample_bulk_upload_csv(self, request, *args, **kwargs):
        if self.bulk_upload_sample_csv:
            return redirect(static(f'csv_examples/{self.bulk_upload_sample_csv}'))
        self.message_user(request, 'Please specify the file name for the sample bulk upload csv.', messages.ERROR)
