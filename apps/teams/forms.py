from django import forms
from django.core.validators import ValidationError
from django.utils.translation import ugettext_lazy as _


class BulkUploadTeamsForm(forms.Form):
    file = forms.FileField(label='CSV File')

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.endswith('.csv') or file.content_type != 'text/csv':
            raise ValidationError(_('Uploaded files must be in .csv format'), code='invalid')
        return file
