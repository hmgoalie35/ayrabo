import csv

from django import forms
from django.contrib import messages
from django.shortcuts import render
from django.views import generic

from ayrabo.utils import pluralize
from ayrabo.utils.admin.forms import AdminBulkUploadForm


class AdminBulkUploadView(generic.FormView):
    form_class = AdminBulkUploadForm
    template_name = 'admin/bulk_upload.html'
    success_url = None
    model = None
    fields = None
    model_form_class = None

    def get_form_value(self, key, value, row):
        func_name = key.replace(' ', '_').lower()
        func = getattr(self, 'get_{}'.format(func_name), None)
        if func is not None:
            return func(value, row)
        return value

    def as_form_data(self, row, count):
        data = {}
        for key, value in row.items():
            key = key.strip()
            value = value.strip()
            new_key = 'form-{}-{}'.format(count, key)
            data[new_key] = self.get_form_value(key, value, row)
        return data

    def clean_data(self, uploaded_file):
        rows = [row.decode() for row in uploaded_file]
        uploaded_file.seek(0)
        reader = csv.DictReader(rows)
        cleaned_data = {}
        raw_data = []
        count = 0
        for row in reader:
            raw_data.append(row)
            form_data = self.as_form_data(row, count)
            cleaned_data.update(form_data)
            count += 1
        cleaned_data['form-TOTAL_FORMS'] = count
        cleaned_data['form-INITIAL_FORMS'] = 0
        return cleaned_data, raw_data

    def get_formset_class(self):
        kwargs = {}
        if self.fields:
            kwargs['fields'] = self.fields
        if self.model_form_class:
            kwargs['form'] = self.model_form_class
        return forms.modelformset_factory(self.model, **kwargs)

    def get_model_form_kwargs(self, data, raw_data):
        return {}

    def form_valid(self, form):
        uploaded_file = form.cleaned_data.get('file')
        cleaned_data, raw_data = self.clean_data(uploaded_file)
        FormSetClass = self.get_formset_class()
        formset = FormSetClass(cleaned_data, form_kwargs=self.get_model_form_kwargs(cleaned_data, raw_data))
        if not formset.is_valid():
            context = self.get_context_data()
            context['formset'] = formset
            context['file'] = uploaded_file
            return render(self.request, self.template_name, context)
        instances = formset.save()
        num_instances = len(instances)
        opts = self.model._meta
        msg = f'Successfully created {num_instances} {pluralize(opts.verbose_name, num_instances, "s")}'
        messages.success(self.request, msg)
        return super().form_valid(form)
