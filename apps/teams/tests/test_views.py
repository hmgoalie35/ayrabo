import os

from django.conf import settings
from django.urls import reverse

from users.tests import UserFactory
from divisions.tests import DivisionFactory
from ayrabo.utils.testing import BaseTestCase
from sports.tests import SportFactory, SportRegistrationFactory


class TeamViewTests(BaseTestCase):
    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory.create(email=self.email, password=self.password, is_staff=True)
        self.ice_hockey = SportFactory(name='Ice Hockey')
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True)
        self.non_staff = UserFactory.create(email='non_staff@ayrabo.com', password=self.password)
        SportRegistrationFactory(user=self.non_staff, sport=self.ice_hockey, is_complete=True)
        self.client.login(email=self.email, password=self.password)
        self.test_file_path = os.path.join(settings.BASE_DIR, 'static', 'csv_examples', 'testing')
        self.midget_minor_aa = DivisionFactory.create(name='Midget Minor AA')

    # GET
    def test_get_not_staff(self):
        self.client.logout()
        self.client.login(email=self.non_staff.email, password=self.password)
        response = self.client.get(reverse('bulk_upload_teams'))
        self.assertRedirects(response, reverse('home'))

    def test_get_status_code_correct_template(self):
        response = self.client.get(reverse('bulk_upload_teams'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teams/team_bulk_upload.html')

    def test_get_context_has_form(self):
        response = self.client.get(reverse('bulk_upload_teams'))
        self.assertIn('form', response.context)

    # POST
    def test_post_not_staff(self):
        self.client.logout()
        self.client.login(email=self.non_staff.email, password=self.password)
        response = self.client.post(reverse('bulk_upload_teams'), {}, follow=True)
        self.assertRedirects(response, reverse('home'))

    def test_post_valid_form(self):
        with open(os.path.join(self.test_file_path, 'valid_team_csv_formatting.csv')) as the_file:
            response = self.client.post(reverse('bulk_upload_teams'), {'file': the_file}, follow=True)
            self.assertHasMessage(response, '1 out of 1 teams successfully created.')

    def test_post_no_csv_headers(self):
        with open(os.path.join(self.test_file_path, 'no_headers.csv')) as the_file:
            response = self.client.post(reverse('bulk_upload_teams'), {'file': the_file}, follow=True)
            self.assertIn(
                    'You must include Team Name, Website and Division as headings in the .csv '
                    'on line 1', response.context['errors'])

            self.assertIn('errors', response.context)
            self.assertTemplateUsed(response, 'teams/team_bulk_upload.html')

    def test_post_team_name_empty(self):
        with open(os.path.join(self.test_file_path, 'team_name_empty.csv')) as the_file:
            response = self.client.post(reverse('bulk_upload_teams'), {'file': the_file}, follow=True)
            self.assertIn("Team Name and/or Division can't be blank on line 1", response.context['errors'])

    def test_post_specified_division_dne(self):
        with open(os.path.join(self.test_file_path, 'division_dne.csv')) as the_file:
            response = self.client.post(reverse('bulk_upload_teams'), {'file': the_file}, follow=True)
            self.assertIn('The division Division DNE does not currently exist, you need to create it under the correct '
                          'league and sport', response.context['errors'])

    def test_post_duplicate_teams(self):
        with open(os.path.join(self.test_file_path, 'duplicate_teams.csv')) as the_file:
            response = self.client.post(reverse('bulk_upload_teams'), {'file': the_file}, follow=True)
            self.assertIn('Validation failed on line 2. Error: Team with this Name and Division already exists.',
                          response.context['errors'])

    def test_post_non_csv_file(self):
        with open(os.path.join(self.test_file_path, 'not_a_csv_file.txt')) as the_file:
            response = self.client.post(reverse('bulk_upload_teams'), {'file': the_file}, follow=True)
            self.assertFormError(response, 'form', 'file', errors=['Uploaded files must be in .csv format'])
