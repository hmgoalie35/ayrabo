import datetime

from django.urls import reverse

from accounts.tests import UserFactory
from common.tests import GenericChoiceFactory
from divisions.tests import DivisionFactory
from escoresheet.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory
from locations.tests import LocationFactory
from managers.tests import ManagerFactory
from seasons.tests import SeasonFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from userprofiles.tests import UserProfileFactory

INPUT_FORMAT = '%m/%d/%Y %I:%M %p'


class HockeyGameCreateViewTests(BaseTestCase):
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
        self.season = SeasonFactory(id=1, league=self.liahl)
        SeasonFactory(id=2, league=self.liahl, start_date=datetime.date(month=12, day=27, year=2016))

        self.sport_registration_url = reverse('sportregistrations:detail', kwargs={'pk': self.sport_registration.id})

        self.start = datetime.datetime(month=12, day=26, year=2017, hour=19, minute=0)
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

    def _login(self, email=None, password=None):
        self.client.login(email=email or self.email, password=password or self.password)

    def _format_url(self, **kwargs):
        return reverse('teams:games:create', kwargs=kwargs)

    def _create_user(self, sport, team, roles, **kwargs):
        user_kwargs = kwargs.get('user')
        user = UserFactory(**user_kwargs)
        sport_registration = SportRegistrationFactory(user=user, sport=sport)
        sport_registration.set_roles(roles)
        manager = ManagerFactory(user=user, team=team)
        return user, sport_registration, manager

    # GET
    def test_login_required(self):
        response = self.client.get(self._format_url(team_pk=1))
        result_url = '{}?next={}'.format(reverse('account_login'), self._format_url(team_pk=1))
        self.assertRedirects(response, result_url)

    def test_not_team_manager(self):
        team = TeamFactory(division=self.mm_aa)
        email = 'user2@example.com'
        self._create_user(self.ice_hockey, team, ['Manager'], user={'email': email, 'password': self.password})
        self._login(email)
        response = self.client.get(self._format_url(team_pk=1))
        self.assertEqual(response.status_code, 404)

    def test_inactive_team_manager(self):
        self.manager.is_active = False
        self.manager.save()
        self._login()
        response = self.client.get(self._format_url(team_pk=1))
        self.assertEqual(response.status_code, 404)

    def test_get(self):
        self._login()
        response = self.client.get(self._format_url(team_pk=1))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'games/hockey_game_create.html')

    def test_get_team_dne(self):
        self._login()
        response = self.client.get(self._format_url(team_pk=999))
        self.assertEqual(response.status_code, 404)

    def test_get_context_data(self):
        self._login()
        response = self.client.get(self._format_url(team_pk=1))
        context = response.context
        self.assertEqual(context['team'].id, self.t1.id)
        self.assertEqual(context['sport_registration_url'], self.sport_registration_url)

    # POST
    def test_valid_post(self):
        self._login()
        response = self.client.post(self._format_url(team_pk=1), data=self.post_data, follow=True)
        self.assertRedirects(response, self.sport_registration_url)
        self.assertHasMessage(response, 'Your game has been created.')

    def test_team_in_url_not_specified(self):
        self._login()
        self.post_data.update({
            'home_team': self.t3.id
        })
        response = self.client.post(self._format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'home_team',
                             ['Green Machine IceCats must be either the home or away team.'])

    def test_home_team_away_team_same(self):
        self._login()
        self.post_data.update({
            'home_team': self.t2.id,
            'away_team': self.t2.id
        })
        response = self.client.post(self._format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'home_team', ['This team must be different than the away team.'])
        self.assertFormError(response, 'form', 'away_team', ['This team must be different than the home team.'])

    def test_end_before_start(self):
        self._login()
        end = self.start - datetime.timedelta(hours=3)
        self.post_data.update({
            'end': end.strftime(INPUT_FORMAT)
        })
        response = self.client.post(self._format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'end', ['Game end must be after game start.'])

    def test_start_not_in_selected_season_year_range(self):
        self._login()
        self.post_data.update({
            'season': 2
        })
        response = self.client.post(self._format_url(team_pk=1), data=self.post_data)
        self.assertFormError(response, 'form', 'start',
                             ['This date and time does not occur during the 2016-2017 Season.'])
