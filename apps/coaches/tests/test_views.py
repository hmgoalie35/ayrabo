import os

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from ayrabo.utils.testing import BaseTestCase
from ayrabo.utils.urls import url_with_query_string
from coaches.models import Coach
from coaches.tests import CoachFactory
from common.tests import WaffleSwitchFactory
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from users.tests import UserFactory


class CoachAdminBulkUploadViewTests(BaseTestCase):
    url = 'admin:coaches_coach_bulk_upload'

    def setUp(self):
        self.url = self.format_url()
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(id=5000, email=self.email, password=self.password, is_staff=True, is_superuser=True)
        self.position = 'head_coach'
        self.sport = SportFactory(name='Ice Hockey')
        self.league = LeagueFactory(sport=self.sport)
        self.division = DivisionFactory(league=self.league)
        self.team = TeamFactory(id=3, division=self.division)

    def test_post_valid_csv(self):
        self.login(user=self.user)
        with open(os.path.join(settings.STATIC_DIR, 'csv_examples', 'bulk_upload_coaches_example.csv')) as f:
            response = self.client.post(self.url, {'file': f}, follow=True)

            coach = Coach.objects.first()
            sport_registrations = SportRegistration.objects.filter(user=self.user)

            self.assertHasMessage(response, 'Successfully created 1 Coach')
            self.assertEqual(coach.user, self.user)
            self.assertEqual(coach.team, self.team)
            self.assertEqual(coach.position, self.position)
            self.assertEqual(coach.is_active, False)
            self.assertEqual(sport_registrations.count(), 1)

    def test_post_invalid_csv(self):
        self.login(user=self.user)
        header = ['user', 'position', 'team', 'is_active']
        row = ['', 'INVALID', 'INVALID', '']
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
            'position',
            ['Select a valid choice. INVALID is not one of the available choices.']
        )
        self.assertFormsetError(
            response,
            'formset',
            0,
            'team',
            ['Select a valid choice. That choice is not one of the available choices.']
        )


class CoachesUpdateViewTests(BaseTestCase):
    url = 'sports:coaches:update'

    def setUp(self):
        self.coach_update_switch = WaffleSwitchFactory(name='coach_update', active=True)
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)
        self.league = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.division = DivisionFactory(name='Midget Minor AA', league=self.league)
        self.team = TeamFactory(name='Green Machine IceCats', division=self.division)
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.COACH)

        self.post_data = {
            'position': Coach.HEAD_COACH
        }
        self.coach = CoachFactory(user=self.user, team=self.team, **self.post_data)
        self.coach_url = self.format_url(slug='ice-hockey', coach_pk=self.coach.pk)

        self.login(user=self.user)

    # General
    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.coach_url)

    def test_sport_dne(self):
        response = self.client.get(self.format_url(slug='non-existent', coach_pk=self.coach.pk))
        self.assert_404(response)

    def test_coach_dne(self):
        response = self.client.get(self.format_url(slug='ice-hockey', coach_pk=99))
        self.assert_404(response)

    def test_has_permission_false(self):
        self.client.logout()
        user = UserFactory(password=self.password)
        self.login(user=user)
        response = self.client.get(self.coach_url)
        self.assert_404(response)

    def test_switch_inactive(self):
        self.coach_update_switch.active = False
        self.coach_update_switch.save()
        response = self.client.get(self.coach_url)
        self.assert_404(response)

    # GET
    def test_get(self):
        response = self.client.get(self.coach_url)
        context = response.context

        self.assert_200(response)
        self.assertTemplateUsed(response, 'coaches/coaches_update.html')
        self.assertEqual(context['coach'].pk, self.coach.pk)

    # POST
    def test_post(self):
        self.post_data.update({'position': Coach.ASSISTANT_COACH})
        response = self.client.post(self.coach_url, data=self.post_data, follow=True)
        self.assertHasMessage(response, 'Your coach information has been updated.')
        self.coach.refresh_from_db()
        self.assertEqual(self.coach.position, Coach.ASSISTANT_COACH)
        url = url_with_query_string(reverse('sports:dashboard', kwargs={'slug': self.ice_hockey.slug}), tab='coach')
        self.assertRedirects(response, url)

    def test_post_nothing_changed(self):
        response = self.client.post(self.coach_url, data=self.post_data, follow=True)
        self.assertNoMessage(response, 'Your coach information has been updated.')
        self.coach.refresh_from_db()
        self.assertEqual(self.coach.position, Coach.HEAD_COACH)
        url = url_with_query_string(reverse('sports:dashboard', kwargs={'slug': self.ice_hockey.slug}), tab='coach')
        self.assertRedirects(response, url)

    def test_post_invalid(self):
        self.post_data.update({'position': ''})
        response = self.client.post(self.coach_url, data=self.post_data, follow=True)
        self.assertFormError(response, 'form', 'position', 'This field is required.')
        self.assertTemplateUsed('coaches/coaches_update.html')
