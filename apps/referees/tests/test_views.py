import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ayrabo.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory
from referees.models import Referee
from sports.models import SportRegistration
from sports.tests import SportFactory
from users.tests import UserFactory


class RefereeAdminBulkUploadViewTests(BaseTestCase):
    url = 'admin:referees_referee_bulk_upload'

    def setUp(self):
        self.url = self.format_url()
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(id=5000, email=self.email, password=self.password, is_staff=True, is_superuser=True)
        self.sport = SportFactory(name='Ice Hockey')
        self.league = LeagueFactory(id=1, sport=self.sport)

    def test_post_valid_csv(self):
        self.login(user=self.user)
        with open(os.path.join(settings.STATIC_DIR, 'csv_examples', 'bulk_upload_referees_example.csv')) as f:
            response = self.client.post(self.url, {'file': f}, follow=True)

            referee = Referee.objects.first()
            sport_registrations = SportRegistration.objects.filter(user=self.user)

            self.assertHasMessage(response, 'Successfully created 1 referee')
            self.assertEqual(referee.user, self.user)
            self.assertEqual(referee.league, self.league)
            self.assertEqual(referee.is_active, False)
            self.assertEqual(sport_registrations.count(), 1)

    def test_post_invalid_csv(self):
        self.login(user=self.user)
        header = ['user', 'league', 'is_active']
        row = ['', 'INVALID', '']
        content = f'{",".join(header)}\n{",".join(row)}'.encode()
        f = SimpleUploadedFile('test.csv', content)
        response = self.client.post(self.url, {'file': f}, follow=True)

        self.assertFormsetError(
            response,
            'formset',
            0,
            'user',
            ['This field is required.']
        )
        self.assertFormsetError(
            response,
            'formset',
            0,
            'league',
            ['Select a valid choice. That choice is not one of the available choices.']
        )
