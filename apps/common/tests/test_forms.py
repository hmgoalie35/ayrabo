from django.core.files.uploadedfile import SimpleUploadedFile

from common.forms import CsvBulkUploadForm
from ayrabo.utils.testing import BaseTestCase


class CsvBulkUploadFormTests(BaseTestCase):
    def setUp(self):
        self.form_cls = CsvBulkUploadForm

    def test_invalid_file_extension(self):
        f = SimpleUploadedFile('test.txt', b'hello world')
        form = self.form_cls({}, {'file': f})
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {
            'file': ['File extension \'txt\' is not allowed. Allowed extensions are: \'csv\'.']
        })

    def test_invalid_csv_file(self):
        # Note the intentionally misleading content_type
        f = SimpleUploadedFile('test.csv', b'#!/usr/bin/python3 print("hello world")', content_type='text/csv')
        form = self.form_cls({}, {'file': f})
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {
            'file': ['Not a valid csv file.']
        })

    def test_valid_csv_file(self):
        f = SimpleUploadedFile('test.csv', b'hello world')
        form = self.form_cls({}, {'file': f})
        self.assertTrue(form.is_valid())
