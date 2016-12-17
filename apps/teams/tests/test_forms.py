import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from escoresheet.utils import BaseTestCase
from teams.forms import BulkUploadTeamsForm


class BulkUploadTeamFormTests(BaseTestCase):
    def setUp(self):
        self.form_cls = BulkUploadTeamsForm

    def test_not_csv(self):
        test_file_path = os.path.join(settings.BASE_DIR, 'static', 'csv_examples', 'testing')

        with open(os.path.join(test_file_path, 'not_a_csv_file.txt'), 'rb') as the_file:
            form = self.form_cls({}, {'file': SimpleUploadedFile(the_file.name, the_file.read())})
            self.assertDictEqual(form.errors, {'file': ['Uploaded files must be in .csv format']})
