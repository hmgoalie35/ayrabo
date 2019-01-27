import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from organizations.tests import OrganizationFactory
from seasons.tests.test_views import AbstractScheduleViewTestCase
from sports.tests import SportFactory
from teams.models import Team
from teams.tests import TeamFactory
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
        liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=ice_hockey)
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


class TeamDetailScheduleViewTests(AbstractScheduleViewTestCase):
    url = 'teams:schedule'

    def setUp(self):
        super().setUp()
        self.formatted_url = self.format_url(team_pk=self.icecats_mm_aa.pk)

    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.formatted_url)

    def test_sport_not_configured(self):
        # Note no season has been configured for this team's league, so the current season will be None.
        team = TeamFactory()
        self.assertSportNotConfigured(self.format_url(team_pk=team.pk))

    # GET
    def test_get(self):
        response = self.client.get(self.formatted_url)
        context = response.context
        team_ids_managed_by_user = [m.team_id for m in self.managers]

        self.assert_200(response)
        self.assertTemplateUsed('teams/team_detail_schedule.html')

        self.assertEqual(context.get('team_display_name'), 'Green Machine IceCats - Midget Minor AA')
        self.assertEqual(context.get('season'), self.current_season)
        self.assertEqual(context.get('schedule_link'), reverse('teams:schedule',
                                                               kwargs={'team_pk': self.icecats_mm_aa.pk}))
        self.assertEqual(context.get('season_rosters_link'), reverse('teams:season_rosters:list',
                                                                     kwargs={'team_pk': self.icecats_mm_aa.pk}))
        self.assertIsNotNone(context.get('past_seasons'))
        self.assertEqual(context.get('page'), 'schedule')
        self.assertEqual(context.get('current_season_page_url'), reverse('teams:schedule',
                                                                         kwargs={'team_pk': self.icecats_mm_aa.pk}))
        self.assertTrue(context.get('can_create_game'))

        self.assertEqual(context.get('active_tab'), 'schedule')
        self.assertListEqual(list(context.get('games')), [self.game1, self.game2])
        self.assertTrue(context.get('has_games'))

        self.assertListEqual(list(context.get('team_ids_managed_by_user')), team_ids_managed_by_user)
        self.assertFalse(context.get('is_scorekeeper'))
        self.assertEqual(context.get('sport'), self.ice_hockey)

    def test_get_past_season(self):
        url = reverse('teams:seasons:schedule',
                      kwargs={'team_pk': self.icecats_mm_aa.pk, 'season_pk': self.previous_season.pk})
        response = self.client.get(url)
        context = response.context

        self.assert_200(response)
        self.assertTemplateUsed('teams/team_detail_schedule.html')

        self.assertEqual(context.get('season'), self.previous_season)
        self.assertEqual(context.get('schedule_link'), reverse('teams:seasons:schedule', kwargs={
            'team_pk': self.icecats_mm_aa.pk, 'season_pk': self.previous_season.pk}))
        self.assertEqual(context.get('season_rosters_link'), reverse('teams:season_rosters:list', kwargs={
            'team_pk': self.icecats_mm_aa.pk}))
        self.assertIsNotNone(context.get('past_seasons'))
        self.assertEqual(context.get('page'), 'schedule')

        # The user is a manager for this team, but the season is expired.
        self.assertFalse(context.get('can_create_game'))
        self.assertFalse(context.get('has_games'))
