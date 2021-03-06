import magic
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


class AdminBulkUploadForm(forms.Form):
    file = forms.FileField(label='CSV File', validators=[FileExtensionValidator(allowed_extensions=['csv'])])

    def is_valid_mime_type(self, mime_type):
        return mime_type in ['application/csv', 'text/csv', 'text/plain']

    def clean_file(self):
        f = self.cleaned_data['file']
        mime_type = magic.from_buffer(f.read(1024), mime=True)
        # Reset the file pointer so subsequent reads of this file don't skip content
        f.seek(0)
        if not self.is_valid_mime_type(mime_type):
            raise ValidationError('Not a valid csv file.', code='invalid')
        return f
