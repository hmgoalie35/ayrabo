import datetime
import os

import pytz
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from accounts.tests import UserFactory
from common.tests import GenericChoiceFactory
from divisions.tests import DivisionFactory
from escoresheet.utils.testing import BaseTestCase
from games.models import HockeyGame
from games.tests import HockeyGameFactory
from leagues.tests import LeagueFactory
from locations.tests import LocationFactory
from managers.tests import ManagerFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from userprofiles.tests import UserProfileFactory

INPUT_FORMAT = '%m/%d/%Y %I:%M %p'


class HockeyGameCreateViewTests(BaseTestCase):
    url = 'teams:games:create'

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'

        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)
        self.t1 = TeamFactory(id=1, name='Green Machine IceCats', division=self.mm_aa)
        self.t2 = TeamFactory(id=2, division=self.mm_aa)
        self.t3 = TeamFactory(id=3, division=self.mm_aa)
        self.t4 = TeamFactory(id=4, division=self.mm_aa)

        self.game_type = GenericChoiceFactory(id=1, short_value='exhibition', long_value='Exhibition', type='game_type',
                                              content_object=self.ice_hockey)
        self.point_value = GenericChoiceFactory(id=2, short_value='2', long_value='2', type='game_point_value',
                                                content_object=self.ice_hockey)

        self.user, self.sport_registration, self.manager = self._create_user(self.ice_hockey, self.t1, ['Manager'],
                                                                             user={'email': self.email,
                                                                                   'password': self.password,
                                                                                   'userprofile': None})
        UserProfileFactory(user=self.user, timezone='US/Eastern')

        self.season_start = datetime.date(month=12, day=27, year=2017)
        self.season = SeasonFactory(id=1, league=self.liahl, start_date=self.season_start)

        self.sport_registration_url = reverse('sportregistrations:detail', kwargs={'pk': self.sport_registration.id})

        self.start = datetime.datetime(month=12, day=27, year=2017, hour=19, minute=0)
        self.end = self.start + datetime.timedelta(hours=3)
        self.post_data = {
            'home_team': self.t1.id,
            'away_team': self.t2.id,
            'type': self.game_type.id,
            'point_value': self.point_value.id,
            'location': LocationFactory().id,
            'start': self.start.strftime(INPUT_FORMAT),
            'end': self.end.strftime(INPUT_FORMAT),
            'timezone': 'US/Pacific',
            'season': self.season.id
        }

    def _create_user(self, sport, team, roles, **kwargs):
        user_kwargs = kwargs.get('user')
        user = UserFactory(**user_kwargs)
        sport_registration = SportRegistrationFactory(user=user, sport=sport)
        sport_registration.set_roles(roles)
        manager = ManagerFactory(user=user, team=team)
        return user, sport_registration, manager

    # GET
    def test_login_required(self):
        response = self.client.get(self.format_url(team_pk=1))
        result_url = '{}?next={}'.format(reverse('account_login'), self.format_url(team_pk=1))
        self.assertRedirects(response, result_url)

    def test_not_team_manager(self):
        team = TeamFactory(division=self.mm_aa)
        email = 'user2@example.com'
        self._create_user(self.ice_hockey, team, ['Manager'], user={'email': email, 'password': self.password})
        self.login(email=email, password=self.password)
        response = self.client.get(self.format_url(team_pk=1))
        self.assertEqual(response.status_code, 404)

    def test_inactive_team_manager(self):
        self.manager.is_active = False
        self.manager.save()
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=1))
        self.assertEqual(response.status_code, 404)

    def test_get(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=1))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'games/game_create.html')

    def test_get_team_dne(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=999))
        self.assertEqual(response.status_code, 404)

    def test_get_context_data(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=1))
        context = response.context
        self.assertEqual(context['team'].id, self.t1.id)

    # Testing some generic functionality in this test...
    def test_get_sport_not_configured(self):
        baseball = SportFactory(name='Baseball')
        email = 'user2@example.com'
        team = TeamFactory(id=5, name='New York Yankees', division__league__sport=baseball)
        self._create_user(baseball, team, ['Manager'], user={'email': email, 'password': self.password})
        self.login(email=email, password=self.password)
        response = self.client.get(self.format_url(team_pk=5))
        self.assertTemplateUsed(response, 'sport_not_configured_msg.html')

    # POST
    def test_valid_post(self):
        self.login(email=self.email, password=self.password)
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data, follow=True)
        self.assertRedirects(response, self.sport_registration_url)
        self.assertHasMessage(response, 'Your game has been created.')

    def test_team_in_url_not_specified(self):
        self.login(email=self.email, password=self.password)
        self.post_data.update({
            'home_team': self.t3.id
        })
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'home_team',
                             ['Green Machine IceCats must be either the home or away team.'])

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
            'end': end.strftime(INPUT_FORMAT)
        })
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'end', ['Game end must be after game start.'])

    def test_game_start_before_season_start(self):
        self.login(email=self.email, password=self.password)
        self.post_data.update({
            'start': (self.season_start - datetime.timedelta(days=7)).strftime(INPUT_FORMAT)
        })
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'start',
                             ['This date does not occur during the 2017-2018 season (12/27/2017-12/27/2018).'])

    def test_game_start_after_season_end(self):
        self.login(email=self.email, password=self.password)
        season_end = self.season.end_date
        self.post_data.update({
            'start': (season_end + datetime.timedelta(days=7)).strftime(INPUT_FORMAT)
        })
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'start',
                             ['This date does not occur during the 2017-2018 season (12/27/2017-12/27/2018).'])

    def test_game_end_before_season_start(self):
        self.login(email=self.email, password=self.password)
        self.post_data.update({
            'end': (self.season_start - datetime.timedelta(days=7)).strftime(INPUT_FORMAT)
        })
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'end',
                             ['This date does not occur during the 2017-2018 season (12/27/2017-12/27/2018).'])

    def test_game_end_after_season_end(self):
        self.login(email=self.email, password=self.password)
        season_end = self.season.end_date
        self.post_data.update({
            'end': (season_end + datetime.timedelta(days=7)).strftime(INPUT_FORMAT)
        })
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'end',
                             ['This date does not occur during the 2017-2018 season (12/27/2017-12/27/2018).'])

    def test_duplicate_game_for_home_team_game_start_tz(self):
        self.login(email=self.email, password=self.password)
        tz = pytz.timezone('US/Eastern')
        start = tz.localize(self.start)
        end = tz.localize(self.end)
        HockeyGameFactory(home_team=self.t1, away_team=self.t2, type=self.game_type, point_value=self.point_value,
                          location=LocationFactory(), start=start, end=end, timezone='US/Pacific', season=self.season)
        response = self.client.post(self.format_url(team_pk=1), data=self.post_data)
        msg = 'This team already has a game for the selected game start and timezone.'
        self.assertFormError(response, 'form', 'home_team', [msg])
        self.assertFormError(response, 'form', 'away_team', [msg])
        self.assertFormError(response, 'form', 'start', [''])
        self.assertFormError(response, 'form', 'timezone', [''])


class HockeyGameListViewTests(BaseTestCase):
    url = 'teams:games:list'

    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(name='Midget Minor AA', league=self.liahl)
        self.icecats = TeamFactory(id=1, name='Green Machine IceCats', division=self.mm_aa)

        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)
        self.sport_registration = SportRegistrationFactory(user=self.user, sport=self.ice_hockey)
        self.sport_registration.set_roles(['Manager'])
        ManagerFactory(user=self.user, team=self.icecats)

    def test_login_required(self):
        url = self.format_url(team_pk=1)
        response = self.client.get(url)
        self.assertRedirects(response, self.get_login_required_url(url))

    def test_get(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=1))
        self.assertTemplateUsed(response, 'games/game_list.html')
        self.assert_200(response)

    def test_team_not_found(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=100))
        self.assert_404(response)

    def test_get_queryset(self):
        t2 = TeamFactory(id=2, division=self.mm_aa)
        t3 = TeamFactory(id=3, division=self.mm_aa)
        t4 = TeamFactory(id=4, division=self.mm_aa)
        game_type = GenericChoiceFactory(id=1, short_value='exhibition', long_value='Exhibition', type='game_type',
                                         content_object=self.ice_hockey)
        point_value = GenericChoiceFactory(id=2, short_value='2', long_value='2', type='game_point_value',
                                           content_object=self.ice_hockey)
        tz = 'US/Eastern'
        season_start = datetime.date(month=8, day=18, year=2017)
        season = SeasonFactory(id=1, league=self.liahl, start_date=season_start)

        # 08/18/2017 @ 07:00PM
        start_base = datetime.datetime.combine(season_start, datetime.time(hour=19, minute=0))
        start_base = pytz.timezone(tz).localize(start_base)

        # 08/25/2017
        g1_start = start_base + datetime.timedelta(weeks=1)

        HockeyGameFactory(id=1, home_team=self.icecats, away_team=t2, type=game_type, point_value=point_value,
                          timezone=tz, season=season, start=g1_start).full_clean()

        # 08/26/2017
        g2_start = g1_start + datetime.timedelta(days=1)
        HockeyGameFactory(id=2, home_team=t2, away_team=self.icecats, type=game_type, point_value=point_value,
                          timezone=tz, season=season, start=g2_start).full_clean()

        # 09/01/2017
        g3_start = g1_start + datetime.timedelta(weeks=1)
        HockeyGameFactory(id=3, home_team=self.icecats, away_team=t3, type=game_type, point_value=point_value,
                          timezone=tz, season=season, start=g3_start).full_clean()
        # 09/02/2017
        g4_start = g3_start + datetime.timedelta(days=1)
        HockeyGameFactory(id=4, home_team=t3, away_team=self.icecats, type=game_type, point_value=point_value,
                          timezone=tz, season=season, start=g4_start).full_clean()

        # 09/09/2017
        g5_start = g4_start + datetime.timedelta(weeks=1)
        HockeyGameFactory(id=5, home_team=t2, away_team=t3, type=game_type, point_value=point_value,
                          timezone=tz, season=season, start=g5_start).full_clean()

        # 09/10/2017
        HockeyGameFactory(id=6, home_team=t2, away_team=t4, type=game_type, point_value=point_value,
                          timezone=tz, season=season, start=g5_start + datetime.timedelta(days=1)).full_clean()

        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=1))

        games = response.context.get('games')
        game_ids = list(games.values_list('id', flat=True))
        self.assertListEqual(game_ids, [1, 3, 2, 4])

    def test_get_context_data(self):
        self.login(email=self.email, password=self.password)
        response = self.client.get(self.format_url(team_pk=1))
        context = response.context
        self.assertTrue(context.get('can_create_game'))
        self.assertEqual(context.get('team'), self.icecats)


class BulkUploadHockeyGamesViewTests(BaseTestCase):
    url = 'bulk_upload_hockeygames'

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.test_file_path = os.path.join(settings.BASE_DIR, 'static', 'csv_examples')
        self.user = UserFactory(email=self.email, password=self.password, is_staff=True)
        sport = SportFactory(name='Ice Hockey')
        league = LeagueFactory(sport=sport, full_name='Long Island Amateur Hockey League')
        division = DivisionFactory(league=league, name='Midget Minor AA')
        TeamFactory(id=35, division=division)
        TeamFactory(id=31, division=division)
        GenericChoiceFactory(id=2, content_object=sport, short_value='exhibition', long_value='Exhibition',
                             type='game_type')
        GenericChoiceFactory(id=7, content_object=sport, short_value='2', long_value='2', type='game_point_value')
        LocationFactory(id=11)
        SeasonFactory(id=10, league=league, start_date=datetime.date(month=8, day=15, year=2017))

    def test_post_valid_csv(self):
        self.client.login(email=self.email, password=self.password)
        with open(os.path.join(self.test_file_path, 'bulk_upload_hockeygames_example.csv')) as f:
            response = self.client.post(self.format_url(), {'file': f}, follow=True)
            self.assertHasMessage(response, 'Successfully created 1 hockeygame object(s)')
            self.assertEqual(HockeyGame.objects.count(), 1)

    def test_post_invalid_csv(self):
        self.client.login(email=self.email, password=self.password)
        content = b'home_team,away_team,type,point_value,location,start,end,timezone,season\n\n35,31,2,7,11,12/26/2017,12/26/2017 09:00 PM,US/Eastern,5'  # noqa
        f = SimpleUploadedFile('test.csv', content)
        response = self.client.post(self.format_url(), {'file': f}, follow=True)
        self.assertEqual(HockeyGame.objects.count(), 0)
        self.assertFormsetError(response, 'formset', 0, 'start', ['Enter a valid date/time.'])
        self.assertFormsetError(response, 'formset', 0, 'season',
                                ['Select a valid choice. That choice is not one of the available choices.'])
