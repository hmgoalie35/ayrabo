import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from organizations.tests import OrganizationFactory
from sports.tests import SportFactory
from teams.models import Team
from users.tests import UserFactory


class BulkUploadTeamsViewTests(BaseTestCase):
    def setUp(self):
        self.url = reverse('bulk_upload_teams')
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.test_file_path = os.path.join(settings.BASE_DIR, 'static', 'csv_examples')
        self.user = UserFactory(email=self.email, password=self.password, is_staff=True)

    def test_post_valid_csv(self):
        ice_hockey = SportFactory(name='Ice Hockey')
        liahl = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=ice_hockey)
        DivisionFactory(name='10U Milner', league=liahl)
        OrganizationFactory(name='Green Machine IceCats', sport=ice_hockey)
        self.client.login(email=self.email, password=self.password)
        with open(os.path.join(self.test_file_path, 'bulk_upload_teams_example.csv')) as f:
            response = self.client.post(self.url, {'file': f}, follow=True)
            self.assertHasMessage(response, 'Successfully created 1 team object(s)')
            self.assertEqual(Team.objects.count(), 1)

    def test_post_invalid_csv(self):
        self.client.login(email=self.email, password=self.password)
        content = b'name, website, division, organization\n\na,b,c,d'
        f = SimpleUploadedFile('test.csv', content)
        response = self.client.post(self.url, {'file': f}, follow=True)
        self.assertEqual(Team.objects.count(), 0)
        self.assertFormsetError(response, 'formset', 0, 'division',
                                ['Select a valid choice. That choice is not one of the available choices.'])
        self.assertFormsetError(response, 'formset', 0, 'organization',
                                ['Select a valid choice. That choice is not one of the available choices.'])
