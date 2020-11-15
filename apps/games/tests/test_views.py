import datetime
import os
from unittest import mock

import pytz
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from common.models import GenericChoice
from common.tests import GenericChoiceFactory
from divisions.tests import DivisionFactory
from games.forms import DATETIME_INPUT_FORMAT
from games.models import HockeyGame
from games.tests import HockeyGameFactory, HockeyGamePlayerFactory
from leagues.tests import LeagueFactory
from locations.tests import LocationFactory
from managers.tests import ManagerFactory
from players.tests import HockeyPlayerFactory
from scorekeepers.tests import ScorekeeperFactory
from seasons.tests import SeasonFactory
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from userprofiles.tests import UserProfileFactory
from users.tests import UserFactory


class HockeyGameCreateViewTests(BaseTestCase):
    url = 'teams:games:create'

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'

        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)
        self.t1 = TeamFactory(id=1, name='Green Machine IceCats', division=self.mm_aa)
        self.t2 = TeamFactory(id=2, division=self.mm_aa)
        self.t3 = TeamFactory(id=3, division=self.mm_aa)
        self.t4 = TeamFactory(id=4, division=self.mm_aa)

        self.game_type = GenericChoiceFactory(id=1, short_value='exhibition', long_value='Exhibition',
                                              type=GenericChoice.GAME_TYPE, content_object=self.ice_hockey)
        self.point_value = GenericChoiceFactory(id=2, short_value='2', long_value='2',
                                                type=GenericChoice.GAME_POINT_VALUE, content_object=self.ice_hockey)

        self.user, self.sport_registrations, self.manager = self._create_user(
            self.ice_hockey,
            self.t1,
            [SportRegistration.MANAGER],
            user={
                'email': self.email,
                'password': self.password,
                'userprofile': None
            }
        )
        UserProfileFactory(user=self.user, timezone='US/Eastern')

        _, self.current_season, _ = self.create_past_current_future_seasons(league=self.liahl)

        self.season_start = datetime.date(month=12, day=27, year=2017)
        self.season = SeasonFactory(
            id=1,
            league=self.liahl,
            start_date=self.season_start,
            teams=[self.t1, self.t2, self.t3, self.t4]
        )

        self.start = datetime.datetime(month=12, day=27, year=2017, hour=19, minute=0)
        self.end = self.start + datetime.timedelta(hours=3)
        self.post_data = {
            'home_team': self.t1.id,
            'away_team': self.t2.id,
            'type': self.game_type.id,
            'point_value': self.point_value.id,
            'location': LocationFactory().id,
            'start': self.start.strftime(DATETIME_INPUT_FORMAT),
            'end': self.end.strftime(DATETIME_INPUT_FORMAT),
            'timezone': 'US/Pacific',
            'season': self.season.id
        }

    def _create_user(self, sport, team, roles, **kwargs):
        user_kwargs = kwargs.get('user')
        user = UserFactory(**user_kwargs)
        sport_registrations = SportRegistration.objects.create_for_user_and_sport(user=user, sport=sport, roles=roles)
        manager = ManagerFactory(user=user, team=team)
        return user, sport_registrations, manager

    # GET
    def test_login_required(self):
        self.assertLoginRequired(self.format_url(team_pk=1))

    def test_not_team_manager(self):
        team = TeamFactory(id=5, division=self.mm_aa)
        email = 'user2@ayrabo.com'
        self._create_user(
            self.ice_hockey,
            team,
            [SportRegistration.MANAGER],
            user={
                'email': email,
                'password': self.password
            }
        )
        self.login(email=email, password=self.password)
        response = self.client.get(self.format_url(team_pk=1))
        self.assert_404(response)

    def test_inactive_team_manager(self):
        self.manager.is_active = False
        self.manager.save()
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=1))
        self.assert_404(response)

    def test_get(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=1))
        context = response.context

        self.assert_200(response)
        self.assertTemplateUsed(response, 'games/game_create.html')
        self.assertEqual(context.get('team'), self.t1)
        self.assertEqual(context.get('team_display_name'), 'Green Machine IceCats - Midget Minor AA')
        self.assertEqual(context.get('active_tab'), 'schedule')
        self.assertIsNotNone(context.get('seasons'))

        # Current season DNE
        self.current_season.delete()
        response = self.client.get(self.format_url(team_pk=1))
        self.assert_200(response)
        self.assertTemplateUsed(response, 'misconfigurations/base.html')
        self.assertAdminEmailSent('Season for Green Machine IceCats misconfigured')

    def test_get_team_dne(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=999))
        self.assert_404(response)

    # Testing some generic functionality in this test...
    def test_get_sport_not_configured(self):
        baseball = SportFactory(name='Baseball')
        email = 'user2@ayrabo.com'
        team = TeamFactory(id=6, name='New York Yankees', division__league__sport=baseball)
        self._create_user(baseball, team, [SportRegistration.MANAGER], user={'email': email, 'password': self.password})
        self.login(email=email, password=self.password)
        response = self.client.get(self.format_url(team_pk=6))
        self.assertTemplateUsed(response, 'misconfigurations/base.html')

    # POST
    def test_valid_post(self):
        self.login(email=self.email, password=self.password)
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data, follow=True)
        url = reverse('teams:schedule', kwargs={'team_pk': self.t1.pk})
        self.assertRedirects(response, url)
        self.assertHasMessage(response, 'Your game has been created.')
        game = HockeyGame.objects.first()
        self.assertEqual(game.team, self.t1)
        self.assertEqual(game.created_by, self.user)

    def test_team_in_url_not_specified(self):
        self.login(email=self.email, password=self.password)
        self.post_data.update({
            'home_team': self.t3.id
        })
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'home_team',
                             ['Green Machine IceCats must be either the home or away team.'])
        self.assertFormError(response, 'form', 'away_team', [''])

    def test_home_team_away_team_same(self):
        self.login(email=self.email, password=self.password)
        self.post_data.update({
            'home_team': self.t2.id,
            'away_team': self.t2.id
        })
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'home_team', ['This team must be different than the away team.'])
        self.assertFormError(response, 'form', 'away_team', ['This team must be different than the home team.'])

    def test_end_before_start(self):
        self.login(email=self.email, password=self.password)
        end = self.start - datetime.timedelta(hours=3)
        self.post_data.update({
            'end': end.strftime(DATETIME_INPUT_FORMAT)
        })
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'end', ['Game end must be after game start.'])

    def test_game_start_before_season_start(self):
        self.login(email=self.email, password=self.password)
        self.post_data.update({
            'start': (self.season_start - datetime.timedelta(days=7)).strftime(DATETIME_INPUT_FORMAT)
        })
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'start',
                             ['This date does not occur during the 12/27/2017-12/27/2018 season.'])

    def test_game_start_after_season_end(self):
        self.login(email=self.email, password=self.password)
        season_end = self.season.end_date
        self.post_data.update({
            'start': (season_end + datetime.timedelta(days=7)).strftime(DATETIME_INPUT_FORMAT)
        })
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'start',
                             ['This date does not occur during the 12/27/2017-12/27/2018 season.'])

    def test_game_end_before_season_start(self):
        self.login(email=self.email, password=self.password)
        self.post_data.update({
            'end': (self.season_start - datetime.timedelta(days=7)).strftime(DATETIME_INPUT_FORMAT)
        })
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'end',
                             ['This date does not occur during the 12/27/2017-12/27/2018 season.'])

    def test_game_end_after_season_end(self):
        self.login(email=self.email, password=self.password)
        season_end = self.season.end_date
        self.post_data.update({
            'end': (season_end + datetime.timedelta(days=7)).strftime(DATETIME_INPUT_FORMAT)
        })
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'end',
                             ['This date does not occur during the 12/27/2017-12/27/2018 season.'])

    def test_duplicate_game_for_home_team_game_start_tz(self):
        self.login(email=self.email, password=self.password)
        tz = pytz.timezone('US/Eastern')
        start = tz.localize(self.start)
        end = tz.localize(self.end)
        HockeyGameFactory(
            home_team=self.t1,
            away_team=self.t2,
            type=self.game_type,
            point_value=self.point_value,
            location=LocationFactory(),
            start=start,
            end=end,
            timezone='US/Pacific',
            season=self.season
        )
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        msg = 'This team already has a game for the selected game start and timezone.'
        self.assertFormError(response, 'form', 'home_team', [msg])
        self.assertFormError(response, 'form', 'away_team', [msg])
        self.assertFormError(response, 'form', 'start', [''])
        self.assertFormError(response, 'form', 'timezone', [''])


class HockeyGameUpdateViewTests(BaseTestCase):
    """
    No need to duplicate all of the form validation logic here, it's already tested in the create view tests. Ideally
    the form validation logic would be in form specific tests so the view tests are more slim, and wouldn't need to
    duplicate anything.
    """
    url = 'teams:games:update'

    def setUp(self):
        self.patcher = mock.patch('django.utils.timezone.now')
        self.mock_now = self.patcher.start()
        self.now = pytz.utc.localize(datetime.datetime(month=12, day=26, year=2017, hour=19, minute=0))
        self.mock_now.return_value = self.now
        self.addCleanup(self.patcher.stop)

        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'

        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)
        self.t1 = TeamFactory(id=7, name='Green Machine IceCats', division=self.mm_aa)
        self.t2 = TeamFactory(id=8, division=self.mm_aa)
        self.t3 = TeamFactory(id=9, division=self.mm_aa)

        self.game_type = GenericChoiceFactory(
            short_value='exhibition',
            long_value='Exhibition',
            type=GenericChoice.GAME_TYPE,
            content_object=self.ice_hockey
        )
        self.point_value = GenericChoiceFactory(
            short_value='2',
            long_value='2',
            type=GenericChoice.GAME_POINT_VALUE,
            content_object=self.ice_hockey
        )

        self.user, self.sport_registrations, self.manager = self._create_user(
            self.ice_hockey,
            self.t1,
            [SportRegistration.MANAGER],
            user={
                'email': self.email,
                'password': self.password,
                'userprofile': None
            }
        )
        timezone = 'US/Eastern'
        us_eastern = pytz.timezone(timezone)
        UserProfileFactory(user=self.user, timezone=timezone)

        _, self.current_season, _ = self.create_past_current_future_seasons(league=self.liahl)

        self.season_start = datetime.date(month=12, day=27, year=2017)
        self.season = SeasonFactory(league=self.liahl, start_date=self.season_start)

        self.start = datetime.datetime(month=12, day=27, year=2017, hour=19, minute=0)
        self.end = self.start + datetime.timedelta(hours=3)
        location = LocationFactory()
        self.game = HockeyGameFactory(
            home_team=self.t1,
            team=self.t1,
            away_team=self.t2,
            type=self.game_type,
            point_value=self.point_value,
            location=location,
            start=us_eastern.localize(self.start),
            end=us_eastern.localize(self.end),
            timezone=timezone,
            season=self.season,
            status=HockeyGame.SCHEDULED
        )
        self.post_data = {
            'home_team': self.t1.id,
            'away_team': self.t2.id,
            'type': self.game_type.id,
            'point_value': self.point_value.id,
            'location': location.id,
            'start': self.start.strftime(DATETIME_INPUT_FORMAT),
            'end': self.end.strftime(DATETIME_INPUT_FORMAT),
            'timezone': timezone,
            'season': self.season.id,
            'status': HockeyGame.SCHEDULED
        }

        self.formatted_url = self.format_url(team_pk=self.t1.id, pk=self.game.id)

    def _create_user(self, sport, team, roles, **kwargs):
        user_kwargs = kwargs.get('user')
        user = UserFactory(**user_kwargs)
        sport_registrations = SportRegistration.objects.create_for_user_and_sport(user=user, sport=sport, roles=roles)
        manager = ManagerFactory(user=user, team=team)
        return user, sport_registrations, manager

    def test_login_required(self):
        self.assertLoginRequired(self.formatted_url)

    def test_not_team_manager(self):
        user, _, _ = self._create_user(self.ice_hockey, self.t3, [SportRegistration.MANAGER],
                                       user={'email': 'user1@ayrabo.com', 'password': self.password})
        self.login(user=user)
        response = self.client.get(self.formatted_url)
        self.assert_404(response)

    def test_team_pk_not_for_game(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=self.t2.id, pk=self.t1.id))
        self.assert_404(response)

    def test_team_dne(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=1000, pk=self.game.id))
        self.assert_404(response)

    def test_sport_not_configured(self):
        """
        It's pretty hard to test this separately for the model and form class.
        """
        team = TeamFactory(id=10)
        SportRegistrationFactory(user=self.user, sport=team.division.league.sport, role=SportRegistration.MANAGER)
        ManagerFactory(user=self.user, team=team)
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=team.pk, pk=self.game.id))
        self.assertTemplateUsed(response, 'misconfigurations/base.html')

    def test_game_dne(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=self.t1.pk, pk=1000))
        self.assert_404(response)

    def test_form_kwargs(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.formatted_url)
        form = response.context.get('form')
        start = form.initial.get('start')
        end = form.initial.get('end')
        self.assertEqual(start, '12/27/2017 07:00 PM')
        self.assertEqual(end, '12/27/2017 10:00 PM')
        self.assertEqual(response.context.get('team'), self.t1)

    def test_form_disabled_game_completed(self):
        self.login(email=self.email, password=self.password)
        self.game.status = HockeyGame.COMPLETED
        self.game.save()
        response = self.client.get(self.formatted_url)
        form = response.context.get('form')
        self.assertTrue(all([v.disabled for k, v in form.fields.items()]))

    def test_form_disabled_end_of_grace_period(self):
        self.login(email=self.email, password=self.password)
        start = pytz.utc.localize(datetime.datetime(month=12, day=24, year=2017, hour=19, minute=0))
        self.game.start = start
        self.game.end = start + datetime.timedelta(hours=2)
        self.game.save()
        response = self.client.get(self.formatted_url)
        form = response.context.get('form')
        self.assertTrue(all([v.disabled for k, v in form.fields.items()]))

    # GET
    def test_get(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.formatted_url)
        context = response.context
        self.assertTemplateUsed(response, 'games/game_update.html')
        self.assert_200(response)
        self.assertEqual(context.get('game'), self.game)
        self.assertEqual(context.get('team'), self.t1)
        self.assertEqual(context.get('team_display_name'), 'Green Machine IceCats - Midget Minor AA')
        self.assertEqual(context.get('active_tab'), 'schedule')
        self.assertIsNotNone(context.get('seasons'))

        # Current season DNE
        self.current_season.delete()
        response = self.client.get(self.formatted_url)
        self.assert_200(response)
        self.assertTemplateUsed(response, 'misconfigurations/base.html')
        self.assertAdminEmailSent('Season for Green Machine IceCats misconfigured')

    # POST
    def test_has_changed_custom_logic(self):
        # Don't mistakenly report the instance has changed if only start and end have changed
        self.login(email=self.email, password=self.password)
        response = self.client.post(self.formatted_url, data=self.post_data, follow=True)
        self.assertNoMessage(response, 'Your game has been updated.')
        self.assertRedirects(response, reverse('teams:schedule', kwargs={'team_pk': self.t1.id}))

    def test_post_valid(self):
        location = LocationFactory()
        # This test case is also making sure the current object is excluded from any unique checks.
        self.login(email=self.email, password=self.password)
        self.post_data.update({'location': location.id})
        response = self.client.post(self.formatted_url, data=self.post_data, follow=True)
        self.assertHasMessage(response, 'Your game has been updated.')
        self.assertRedirects(response, reverse('teams:schedule', kwargs={'team_pk': self.t1.id}))
        self.game.refresh_from_db()
        self.assertEqual(self.game.location.id, location.id)

    def test_post_change_timezone(self):
        self.login(email=self.email, password=self.password)
        tz = 'US/Pacific'
        self.post_data.update({'timezone': tz})
        self.client.post(self.formatted_url, data=self.post_data, follow=True)
        self.game.refresh_from_db()
        self.assertEqual(self.game.start_formatted, '12/27/2017 07:00 PM PST')
        self.assertEqual(self.game.end_formatted, '12/27/2017 10:00 PM PST')
        self.assertEqual(self.game.timezone, tz)

    def test_post_invalid(self):
        self.login(email=self.email, password=self.password)
        self.post_data.pop('home_team')
        response = self.client.post(self.formatted_url, data=self.post_data)
        self.assertFormError(response, 'form', 'home_team', ['This field is required.'])

    def test_post_change_home_team(self):
        self.game.home_team = self.t2
        self.game.away_team = self.t1
        self.game.save()
        HockeyGamePlayerFactory(
            team=self.t2,
            player=HockeyPlayerFactory(sport=self.ice_hockey, team=self.t2),
            game=self.game
        )
        self.login(email=self.email, password=self.password)
        self.post_data.update({'home_team': self.t3.id, 'away_team': self.t1.id})

        self.client.post(self.formatted_url, data=self.post_data, follow=True)
        self.game.refresh_from_db()
        self.assertEqual(self.game._get_game_players(self.t2).count(), 0)

    def test_post_change_away_team(self):
        HockeyGamePlayerFactory(
            team=self.t2,
            player=HockeyPlayerFactory(sport=self.ice_hockey, team=self.t2),
            game=self.game
        )
        self.login(email=self.email, password=self.password)
        self.post_data.update({'away_team': self.t3.id})

        self.client.post(self.formatted_url, data=self.post_data, follow=True)
        self.game.refresh_from_db()
        self.assertEqual(self.game._get_game_players(self.t2).count(), 0)


class HockeyGameScoresheetViewTests(BaseTestCase):
    url = 'sports:games:scoresheet'

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'

        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)
        self.t1 = TeamFactory(id=11, name='Green Machine IceCats', division=self.mm_aa)
        self.t2 = TeamFactory(id=12, name='Aviator Gulls', division=self.mm_aa)

        self.game_type = GenericChoiceFactory(
            short_value='exhibition',
            long_value='Exhibition',
            type=GenericChoice.GAME_TYPE,
            content_object=self.ice_hockey
        )
        self.point_value = GenericChoiceFactory(
            short_value='2',
            long_value='2',
            type=GenericChoice.GAME_POINT_VALUE,
            content_object=self.ice_hockey
        )

        timezone = 'US/Eastern'
        us_eastern = pytz.timezone(timezone)

        self.user = UserFactory(email=self.email, password=self.password, userprofile__timezone=timezone)

        self.season_start = datetime.date(month=12, day=27, year=2017)
        self.season = SeasonFactory(league=self.liahl, start_date=self.season_start)

        self.start = datetime.datetime(month=12, day=27, year=2017, hour=19, minute=0)
        self.end = self.start + datetime.timedelta(hours=3)
        location = LocationFactory()
        self.game = HockeyGameFactory(
            id=1,
            home_team=self.t1,
            team=self.t1,
            away_team=self.t2,
            type=self.game_type,
            point_value=self.point_value,
            location=location,
            start=us_eastern.localize(self.start),
            end=us_eastern.localize(self.end),
            timezone=timezone,
            season=self.season,
            status=HockeyGame.SCHEDULED
        )
        self.formatted_url = self.format_url(slug=self.ice_hockey.slug, game_pk=1)
        self.login(user=self.user)

    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.formatted_url)

    def test_get_sport(self):
        response = self.client.get(self.formatted_url)
        self.assert_200(response)

        response = self.client.get(self.format_url(slug='baseball', game_pk=1))
        self.assert_404(response)

    def test_get_success_url(self):
        response = self.client.post(self.formatted_url, data={'status': 'scheduled'})

        expected = reverse('sports:games:scoresheet', kwargs={'slug': self.ice_hockey.slug, 'game_pk': self.game.pk})
        self.assertRedirects(response, expected)

    def test_get_object(self):
        # Sport misconfigured
        SportFactory(name='soccer')
        self.assertSportNotConfigured(self.format_url(slug='soccer', game_pk=1))

        # Game DNE
        response = self.client.get(self.format_url(slug=self.ice_hockey.slug, game_pk=2222))
        self.assert_404(response)

        # Game exists
        response = self.client.get(self.formatted_url)
        self.assert_200(response)
        self.assertEqual(response.context['game'], self.game)

    def test_get(self):
        pass

    def test_post(self):
        pass


class GameRostersUpdateViewTests(BaseTestCase):
    url = 'sports:games:rosters:update'

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'

        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)
        self.t1 = TeamFactory(id=13, name='Green Machine IceCats', division=self.mm_aa)
        self.t2 = TeamFactory(id=14, name='Aviator Gulls', division=self.mm_aa)

        self.game_type = GenericChoiceFactory(short_value='exhibition', long_value='Exhibition',
                                              type=GenericChoice.GAME_TYPE, content_object=self.ice_hockey)
        self.point_value = GenericChoiceFactory(short_value='2', long_value='2', type=GenericChoice.GAME_POINT_VALUE,
                                                content_object=self.ice_hockey)

        timezone = 'US/Eastern'
        us_eastern = pytz.timezone(timezone)

        self.user = UserFactory(email=self.email, password=self.password, userprofile__timezone=timezone)

        self.season_start = datetime.date(month=12, day=27, year=2017)
        self.season = SeasonFactory(league=self.liahl, start_date=self.season_start)

        self.start = datetime.datetime(month=12, day=27, year=2017, hour=19, minute=0)
        self.end = self.start + datetime.timedelta(hours=3)
        location = LocationFactory()
        self.game = HockeyGameFactory(id=1, home_team=self.t1, team=self.t1, away_team=self.t2, type=self.game_type,
                                      point_value=self.point_value, location=location,
                                      start=us_eastern.localize(self.start), end=us_eastern.localize(self.end),
                                      timezone=timezone, season=self.season, status=HockeyGame.SCHEDULED)
        self.formatted_url = self.format_url(slug='ice-hockey', game_pk=1)
        self.login(user=self.user)

    # General
    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.formatted_url)

    def test_has_permission_home_team_manager(self):
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.MANAGER)
        ManagerFactory(user=self.user, team=self.t1)

        response = self.client.get(self.formatted_url)
        self.assert_200(response)

    def test_has_permission_away_team_manager(self):
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.MANAGER)
        ManagerFactory(user=self.user, team=self.t2)

        response = self.client.get(self.formatted_url)
        self.assert_200(response)

    def test_has_permission_scorekeeper(self):
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.SCOREKEEPER)
        ScorekeeperFactory(user=self.user, sport=self.ice_hockey)

        response = self.client.get(self.formatted_url)
        self.assert_200(response)

    def test_has_permission_inactive_roles(self):
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.MANAGER)
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.SCOREKEEPER)
        ManagerFactory(user=self.user, team=self.t1, is_active=False)
        ScorekeeperFactory(user=self.user, sport=self.ice_hockey, is_active=False)

        response = self.client.get(self.formatted_url)
        self.assert_404(response)

    def test_has_permission_false(self):
        self.client.logout()
        user = UserFactory()
        SportRegistrationFactory(user=user, sport=self.ice_hockey, role=SportRegistration.MANAGER)
        # This user is a manager for some random team.
        ManagerFactory(user=user)
        self.login(user=user)

        response = self.client.get(self.formatted_url)
        self.assert_404(response)

    def test_game_dne(self):
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.MANAGER)
        ManagerFactory(user=self.user, team=self.t1)

        response = self.client.get(self.format_url(slug='ice-hockey', game_pk=1000))
        self.assert_404(response)

    def test_sport_not_configured(self):
        sport = SportFactory()
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.MANAGER)
        ManagerFactory(user=self.user, team=self.t1)

        response = self.client.get(self.format_url(slug=sport.slug, game_pk=1))

        self.assertTemplateUsed(response, 'misconfigurations/base.html')

    def test_sport_dne(self):
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.MANAGER)
        ManagerFactory(user=self.user, team=self.t1)

        response = self.client.get(self.format_url(slug='i-dont-exist', game_pk=1))

        self.assert_404(response)

    # GET
    @mock.patch('django.utils.timezone.now')
    def test_get(self, mock_now):
        mock_now.return_value = pytz.utc.localize(datetime.datetime(month=12, day=26, year=2017, hour=19, minute=0))
        SportRegistrationFactory(user=self.user, sport=self.ice_hockey, role=SportRegistration.MANAGER)
        ManagerFactory(user=self.user, team=self.t1)

        response = self.client.get(self.formatted_url)

        context = response.context
        self.assert_200(response)
        self.assertTemplateUsed(response, 'games/game_rosters_update.html')
        self.assertEqual(context.get('game').id, 1)
        self.assertEqual(context.get('home_team'), self.game.home_team)
        self.assertEqual(context.get('home_team_name'), 'Green Machine IceCats Midget Minor AA')
        self.assertEqual(context.get('away_team'), self.game.away_team)
        self.assertEqual(context.get('away_team_name'), 'Aviator Gulls Midget Minor AA')
        self.assertTrue(context.get('can_update_home_team_roster'))
        self.assertFalse(context.get('can_update_away_team_roster'))
        self.assertEqual(context.get('sport'), self.ice_hockey)


class HockeyGameAdminBulkUploadViewTests(BaseTestCase):
    url = 'admin:games_hockeygame_bulk_upload'

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(id=1, email=self.email, password=self.password, is_staff=True, is_superuser=True)
        sport = SportFactory(name='Ice Hockey')
        league = LeagueFactory(sport=sport, name='Long Island Amateur Hockey League')
        division = DivisionFactory(league=league, name='Midget Minor AA')
        TeamFactory(id=35, division=division)
        TeamFactory(id=31, division=division)
        GenericChoiceFactory(
            id=2,
            content_object=sport,
            short_value='exhibition',
            long_value='Exhibition',
            type=GenericChoice.GAME_TYPE
        )
        GenericChoiceFactory(
            id=7,
            content_object=sport,
            short_value='2',
            long_value='2',
            type=GenericChoice.GAME_POINT_VALUE
        )
        LocationFactory(id=11)
        SeasonFactory(id=10, league=league, start_date=datetime.date(month=8, day=15, year=2017))

    def test_post_valid_csv(self):
        self.login(email=self.email, password=self.password)
        with open(os.path.join(settings.STATIC_DIR, 'csv_examples', 'bulk_upload_hockeygames_example.csv')) as f:
            response = self.client.post(self.format_url(), {'file': f}, follow=True)
            self.assertHasMessage(response, 'Successfully created 1 hockey game')
            self.assertEqual(HockeyGame.objects.count(), 1)

    def test_post_invalid_csv(self):
        self.login(email=self.email, password=self.password)
        header = ['home_team', 'away_team', 'team', 'type', 'point_value', 'location', 'start', 'end', 'timezone',
                  'season', 'created_by']
        row = ['35', '31', '35', '2', '7', '11', '12/26/2017', '12/26/2017 09:00 PM', 'US/Eastern', '5', '1']
        content = f'{",".join(header)}\n\n{",".join(row)}'.encode()
        f = SimpleUploadedFile('test.csv', content)
        response = self.client.post(self.format_url(), {'file': f}, follow=True)
        self.assertEqual(HockeyGame.objects.count(), 0)
        self.assertFormsetError(response, 'formset', 0, 'start', ['Enter a valid date/time.'])
        self.assertFormsetError(
            response,
            'formset',
            0,
            'season',
            ['Select a valid choice. That choice is not one of the available choices.']
        )
