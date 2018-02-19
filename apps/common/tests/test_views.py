import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from users.tests import UserFactory
from divisions.tests import DivisionFactory
from ayrabo.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


# Am testing this base view via the `PlayersCreateView`
class BaseCreateRelatedObjectsViewTests(BaseTestCase):
    def _format_url(self, role, **kwargs):
        return reverse(self.url.format(role=role), kwargs=kwargs)

    @classmethod
    def setUpTestData(cls):
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.basketball = SportFactory(name='Basketball')

    def setUp(self):
        self.url = 'sportregistrations:{role}:create'
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.post_data = {
            'players-TOTAL_FORMS': 1,
            'players-INITIAL_FORMS': 0,
            'players-MIN_NUM_FORMS': 1,
            'players-MAX_NUM_FORMS': 10
        }

        self.user = UserFactory(email=self.email, password=self.password)

        self.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.division = DivisionFactory(name='Midget Minor AA', league=self.league)
        self.team = TeamFactory(name='Green Machine IceCats', division=self.division)

        self.sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=False)
        self.sr_2 = SportRegistrationFactory(user=self.user, sport=self.baseball, is_complete=False)
        self.sr.set_roles(['Player', 'Coach'])
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        url = self._format_url('players', pk=self.sr.id)
        response = self.client.get(url)
        result_url = '{}?next={}'.format(reverse('account_login'), url)
        self.assertRedirects(response, result_url)

    def test_get(self):
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        self.assertTemplateUsed(response, 'players/players_create.html')
        self.assertEqual(response.status_code, 200)

    def test_get_not_obj_owner(self):
        self.client.logout()
        user = UserFactory(password=self.password)
        SportRegistrationFactory(user=user, is_complete=True)
        self.client.login(email=user.email, password=self.password)
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        self.assertEqual(response.status_code, 404)

    # POST
    def test_post_anonymous_user(self):
        self.client.logout()
        url = self._format_url('players', pk=self.sr.id)
        response = self.client.post(url, data={}, follow=True)
        result_url = '{}?next={}'.format(reverse('account_login'), url)
        self.assertRedirects(response, result_url)

    def test_post_not_obj_owner(self):
        self.client.logout()
        user = UserFactory(password=self.password)
        SportRegistrationFactory(user=user, is_complete=True)
        self.client.login(email=user.email, password=self.password)
        response = self.client.post(self._format_url('players', pk=self.sr.id), data={}, follow=True)
        self.assertEqual(response.status_code, 404)


# Am testing this base class via BulkUploadLocationsView. Tests to see if objects are actually created happen in the
# respective subclasses.
class CsvBulkUploadViewTests(BaseTestCase):
    def setUp(self):
        self.url = reverse('bulk_upload_locations')
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.test_file_path = os.path.join(settings.BASE_DIR, 'static', 'csv_examples')
        self.user = UserFactory(email=self.email, password=self.password, is_staff=True)

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        result_url = '{}?next={}'.format(reverse('admin:login'), self.url)
        self.assertRedirects(response, result_url)

    def test_staff_member_required(self):
        email = 'user1@ayrabo.com'
        password = 'myweakpassword'
        UserFactory(email=email, password=password, is_staff=False)
        self.client.login(email=email, password=password)

        response = self.client.get(self.url)
        result_url = '{}?next={}'.format(reverse('admin:login'), self.url)
        self.assertRedirects(response, result_url)

    def test_get(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'common/admin_bulk_upload.html')
        self.assertIsNotNone(response.context['form'])

    def test_post(self):
        self.client.login(email=self.email, password=self.password)
        f = SimpleUploadedFile('test.csv', b'hello world')
        response = self.client.post(self.url, {'file': f})
        self.assertRedirects(response, self.url)
