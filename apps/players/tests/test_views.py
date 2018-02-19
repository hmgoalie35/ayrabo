from django.core import mail
from django.urls import reverse

from accounts.tests import UserFactory
from divisions.tests import DivisionFactory
from ayrabo.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory
from players.forms import HockeyPlayerForm
from players.formset_helpers import HockeyPlayerFormSetHelper
from players.models import HockeyPlayer
from players.tests import HockeyPlayerFactory, BaseballPlayerFactory
from referees.tests import RefereeFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


class PlayersCreateViewTests(BaseTestCase):
    def _format_url(self, role, **kwargs):
        return reverse(self.url.format(role=role), kwargs=kwargs)

    @classmethod
    def setUpTestData(cls):
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.basketball = SportFactory(name='Basketball')

    def setUp(self):
        self.url = 'sportregistrations:{role}:create'
        self.email = 'user@example.com'
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

        self.baseball_league = LeagueFactory(full_name='Major League Baseball', sport=self.baseball)
        self.baseball_division = DivisionFactory(name='American League East', league=self.baseball_league)
        self.baseball_team = TeamFactory(name='New York Yankees', division=self.baseball_division)

        self.sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=False)
        self.sr_2 = SportRegistrationFactory(user=self.user, sport=self.baseball, is_complete=False)
        self.sr.set_roles(['Player', 'Coach'])
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_template_name(self):
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'players/players_create.html')

    def test_get_form_class(self):
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        form_cls = response.context['formset'].forms[0]
        self.assertIsInstance(form_cls, HockeyPlayerForm)

    def test_get_formset_prefix(self):
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        formset = response.context['formset']
        self.assertEqual(formset.prefix, 'players')

    def test_get_model_class(self):
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        self.assertIs(response.context['formset'].model, HockeyPlayer)

    def test_get_formset_helper_class(self):
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        self.assertIs(response.context['helper'], HockeyPlayerFormSetHelper)

    def test_get_role(self):
        response = self.client.get(self._format_url('players', pk=self.sr.id))
        self.assertEqual(response.context['role'], 'Player')

    def test_get_registered_for_all(self):
        self.sr.set_roles(['Player'])
        self.sr.is_complete = True
        self.sr.save()
        HockeyPlayerFactory(user=self.user, team=self.team, sport=self.ice_hockey)
        self.sr_2.is_complete = True
        self.sr_2.save()
        response = self.client.get(self._format_url('players', pk=self.sr.id), follow=True)
        self.assertHasMessage(response, 'You have already registered for all available teams.')
        self.assertRedirects(response, self.sr.get_absolute_url())

    def test_get_sport_not_configured(self):
        self.sr.is_complete = True
        self.sr.save()
        self.sr_2.is_complete = True
        self.sr_2.save()
        sr = SportRegistrationFactory(user=self.user, is_complete=False)
        sr.set_roles(['Player'])
        response = self.client.get(self._format_url('players', pk=sr.id), follow=True)
        self.assertTemplateUsed(response, 'sport_not_configured_msg.html')
        msg = "{sport} hasn't been configured correctly in our system. " \
              "If you believe this is an error please contact us.".format(sport=sr.sport.name)
        self.assertEqual(response.context['message'], msg)
        self.assertEqual(len(mail.outbox), 1)

    # POST
    def test_post_one_valid_form(self):
        """
        The sport registration has 2 roles, so it won't be completed but will redirect to the coaches creation page.
        """
        form_data = {
            'players-0-team': self.team.id,
            'players-0-jersey_number': 23,
            'players-0-position': 'LW',
            'players-0-handedness': 'Right'
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('players', pk=self.sr.id), data=self.post_data, follow=True)
        player = HockeyPlayer.objects.filter(user=self.user, team=self.team)
        self.assertTrue(player.exists())
        self.assertRedirects(response, self._format_url('coaches', pk=self.sr.id))
        self.assertHasMessage(response, 'You have been registered as a player for the Green Machine IceCats.')

    def test_post_two_valid_forms(self):
        """
        The sport registration has 2 roles, so it won't be completed but will redirect to the coaches creation page.
        """
        t1 = TeamFactory(division__league__sport=self.ice_hockey)
        form_data = {
            'players-0-team': self.team.id,
            'players-0-jersey_number': 23,
            'players-0-position': 'LW',
            'players-0-handedness': 'Right',
            'players-1-team': t1.id,
            'players-1-jersey_number': 33,
            'players-1-position': 'G',
            'players-1-handedness': 'Left',
            'players-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('players', pk=self.sr.id), data=self.post_data, follow=True)
        players = HockeyPlayer.objects.filter(user=self.user)
        self.assertEqual(players.count(), 2)
        self.assertRedirects(response, self._format_url('coaches', pk=self.sr.id))
        self.assertHasMessage(response,
                              'You have been registered as a player for the Green Machine IceCats, {}.'.format(t1.name))

    def test_post_three_valid_forms(self):
        """
        The sport registration has 2 roles, so it won't be completed but will redirect to the coaches creation page.
        """
        l1 = LeagueFactory(full_name='National Hockey League', sport=self.ice_hockey)
        l2 = LeagueFactory(sport=self.ice_hockey)
        d1 = DivisionFactory(league=l1)
        d2 = DivisionFactory(league=l2)
        t1 = TeamFactory(division=d1)
        t2 = TeamFactory(division=d2)
        form_data = {
            'players-0-team': self.team.id,
            'players-0-jersey_number': 23,
            'players-0-position': 'LW',
            'players-0-handedness': 'Right',
            'players-1-team': t1.id,
            'players-1-jersey_number': 33,
            'players-1-position': 'G',
            'players-1-handedness': 'Left',
            'players-2-team': t2.id,
            'players-2-jersey_number': 38,
            'players-2-position': 'G',
            'players-2-handedness': 'Left',
            'players-TOTAL_FORMS': 3,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('players', pk=self.sr.id), data=self.post_data, follow=True)
        players = HockeyPlayer.objects.filter(user=self.user)
        self.assertEqual(players.count(), 3)
        self.assertRedirects(response, self._format_url('coaches', pk=self.sr.id))
        self.assertHasMessage(response,
                              'You have been registered as a player for the Green Machine IceCats, {}, {}.'.format(
                                  t1.name, t2.name))

    def test_post_two_forms_same_team(self):
        form_data = {
            'players-0-team': self.team.id,
            'players-0-jersey_number': 23,
            'players-0-position': 'LW',
            'players-0-handedness': 'Right',
            'players-1-team': self.team.id,
            'players-1-jersey_number': 33,
            'players-1-position': 'G',
            'players-1-handedness': 'Left',
            'players-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('players', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 1, 'team',
                                '{} has already been selected. Please choose another team or remove this form.'.format(
                                        self.team.name))

    def test_post_already_registered_for_team(self):
        self.sr.set_roles(['Player'])
        TeamFactory(name='My Team', division=self.division)
        HockeyPlayerFactory(user=self.user, team=self.team, sport=self.ice_hockey)
        self.sr.is_complete = True
        self.sr.save()
        BaseballPlayerFactory(user=self.user, team=self.team, sport=self.baseball)
        self.sr_2.is_complete = True
        self.sr_2.save()
        form_data = {
            'players-0-team': self.team.id,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('players', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'team',
                                'Select a valid choice. That choice is not one of the available choices.')

    def test_post_one_invalid_form(self):
        form_data = {
            'players-0-position': 'LW',
            'players-TOTAL_FORMS': 1,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('players', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'handedness', 'This field is required.')
        self.assertFormsetError(response, 'formset', 0, 'team', 'This field is required.')
        self.assertFormsetError(response, 'formset', 0, 'jersey_number', 'This field is required.')

    def test_post_two_invalid_forms(self):
        form_data = {
            'players-0-position': 'LW',
            'players-0-handedness': 'Right',
            'players-1-position': 'LW',
            'players-1-handedness': 'Left',
            'players-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('players', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'team', 'This field is required.')
        self.assertFormsetError(response, 'formset', 0, 'jersey_number', 'This field is required.')
        self.assertFormsetError(response, 'formset', 1, 'team', 'This field is required.')
        self.assertFormsetError(response, 'formset', 1, 'jersey_number', 'This field is required.')

    def test_post_empty_added_form(self):
        form_data = {
            'players-0-team': self.team.id,
            'players-0-jersey_number': 23,
            'players-0-position': 'LW',
            'players-0-handedness': 'Right',
            'players-1-team': '',
            'players-1-jersey_number': '',
            'players-1-position': '',
            'players-1-handedness': '',
            'players-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('players', pk=self.sr.id), data=self.post_data, follow=True)
        url = 'sportregistrations:{role}:create'.format(role='coaches')
        self.assertRedirects(response, reverse(url, kwargs={'pk': self.sr.id}))

    def test_next_sport_registration_fetched(self):
        self.sr.set_roles(['Player'])
        form_data = {
            'players-0-team': self.team.id,
            'players-0-jersey_number': 23,
            'players-0-position': 'LW',
            'players-0-handedness': 'Right',
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('players', pk=self.sr.id), data=self.post_data, follow=True)
        url = 'sportregistrations:{role}:create'.format(role='players')
        self.assertRedirects(response, reverse(url, kwargs={'pk': self.sr_2.id}))

    def test_no_remaining_sport_registrations(self):
        self.sr.set_roles(['Player'])
        self.sr_2.set_roles(['Player'])
        form_data = {
            'players-0-team': self.team.id,
            'players-0-jersey_number': 23,
            'players-0-position': 'LW',
            'players-0-handedness': 'Right',
        }
        self.post_data.update(form_data)
        self.client.post(self._format_url('players', pk=self.sr.id), data=self.post_data, follow=True)

        league = LeagueFactory(full_name='Major League Baseball', sport=self.baseball)
        division = DivisionFactory(name='American League Central', league=league)
        team = TeamFactory(name='Detroit Tigers', division=division)
        self.post_data.update({
            'players-0-team': team.id,
            'players-0-jersey_number': 23,
            'players-0-position': 'C',
            'players-0-catches': 'Right',
            'players-0-bats': 'Right',
        })

        response = self.client.post(self._format_url('players', pk=self.sr_2.id), data=self.post_data, follow=True)

        self.assertRedirects(response, reverse('home'))

    def test_post_add_player_role_valid_form(self):
        self.sr.set_roles(['Referee'])
        self.sr.is_complete = True
        self.sr.save()
        RefereeFactory(user=self.user, league=self.league)
        self.sr_2.is_complete = True
        self.sr_2.save()
        form_data = {
            'players-0-team': self.team.id,
            'players-0-jersey_number': 33,
            'players-0-position': 'G',
            'players-0-handedness': 'Left'
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('players', pk=self.sr.id), data=self.post_data, follow=True)
        player = HockeyPlayer.objects.filter(user=self.user, team=self.team)
        self.assertTrue(player.exists())
        self.sr.refresh_from_db()
        self.assertTrue(self.sr.has_role('Player'))
        self.assertHasMessage(response, 'You have been registered as a player for the Green Machine IceCats.')

    def test_post_add_player_role_invalid_form(self):
        self.sr.set_roles(['Referee'])
        self.sr.is_complete = True
        self.sr.save()
        RefereeFactory(user=self.user, league=self.league)
        self.sr_2.is_complete = True
        self.sr_2.save()
        form_data = {
            'players-0-team': -1,
            'players-0-jersey_number': 33,
            'players-0-position': 'G',
            'players-0-handedness': 'Left'
        }
        self.post_data.update(form_data)
        self.client.post(self._format_url('players', pk=self.sr.id), data=self.post_data, follow=True)
        player = HockeyPlayer.objects.filter(user=self.user, team=self.team)
        self.assertFalse(player.exists())
        self.sr.refresh_from_db()
        self.assertFalse(self.sr.has_role('Player'))

    def test_post_registered_for_all(self):
        self.sr.set_roles(['Player'])
        self.sr.is_complete = True
        self.sr.save()
        HockeyPlayerFactory(user=self.user, team=self.team, sport=self.ice_hockey)
        self.sr_2.is_complete = True
        self.sr_2.save()
        response = self.client.post(self._format_url('players', pk=self.sr.id), data={}, follow=True)
        self.assertHasMessage(response, 'You have already registered for all available teams.')
        self.assertRedirects(response, self.sr.get_absolute_url())


class PlayerUpdateViewTests(BaseTestCase):
    def _format_url(self, **kwargs):
        return reverse(self.url, kwargs=kwargs)

    @classmethod
    def setUpTestData(cls):
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.url = 'sportregistrations:players:update'
        cls.email = 'user@example.com'
        cls.password = 'myweakpassword'
        cls.user = UserFactory(email=cls.email, password=cls.password)
        cls.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.division = DivisionFactory(name='Midget Minor AA', league=cls.league)
        cls.team = TeamFactory(name='Green Machine IceCats', division=cls.division)

        cls.baseball_league = LeagueFactory(full_name='Major League Baseball', sport=cls.baseball)
        cls.baseball_division = DivisionFactory(name='American League East', league=cls.baseball_league)
        cls.baseball_team = TeamFactory(name='New York Yankees', division=cls.baseball_division)
        cls.baseball_player = BaseballPlayerFactory(user=cls.user, sport=cls.baseball, team=cls.baseball_team,
                                                    jersey_number=25)

        cls.sr = SportRegistrationFactory(user=cls.user, sport=cls.ice_hockey, is_complete=True)
        cls.sr_2 = SportRegistrationFactory(user=cls.user, sport=cls.baseball, is_complete=True)
        cls.sr.set_roles(['Player'])
        cls.sr_2.set_roles(['Player'])

    def setUp(self):
        self.post_data = {
            'jersey_number': 23,
            'position': 'LW',
            'handedness': 'Left'
        }
        self.player = HockeyPlayerFactory(user=self.user, sport=self.ice_hockey, team=self.team, **self.post_data)
        self.hockeyplayer_url = self._format_url(pk=self.sr.pk, player_pk=self.player.pk)
        self.baseballplayer_url = self._format_url(pk=self.sr_2.pk, player_pk=self.player.pk)

        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous(self):
        self.client.logout()
        response = self.client.get(self.hockeyplayer_url)
        result_url = '{}?next={}'.format(reverse('account_login'), self.hockeyplayer_url)
        self.assertRedirects(response, result_url)

    def test_get(self):
        response = self.client.get(self.hockeyplayer_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'players/players_update.html')
        context = response.context
        self.assertIsNotNone(context['player'])
        self.assertIsNotNone(context['sport_registration'])
        self.assertIsNotNone(context['form'])

    def test_get_sport_reg_dne(self):
        response = self.client.get(self._format_url(pk=99, player_pk=self.player.pk))
        self.assertEqual(response.status_code, 404)

    def test_get_player_obj_dne(self):
        response = self.client.get(self._format_url(pk=self.sr.pk, player_pk=99))
        self.assertEqual(response.status_code, 404)

    def test_get_not_obj_owner(self):
        self.client.logout()
        user = UserFactory(password=self.password)
        SportRegistrationFactory(user=user, sport=self.ice_hockey)
        self.client.login(email=user.email, password=self.password)
        response = self.client.get(self.hockeyplayer_url)
        self.assertEqual(response.status_code, 404)

    # POST
    def test_post(self):
        self.post_data.update({'jersey_number': 99})
        response = self.client.post(self.hockeyplayer_url, data=self.post_data, follow=True)
        self.assertHasMessage(response, 'Your player information has been updated.')
        self.player.refresh_from_db()
        self.assertEqual(self.player.jersey_number, 99)
        self.assertRedirects(response, self.sr.get_absolute_url())

    def test_post_nothing_changed(self):
        response = self.client.post(self.hockeyplayer_url, data=self.post_data, follow=True)
        self.assertNoMessage(response, 'Your player information has been updated.')
        self.player.refresh_from_db()
        self.assertEqual(self.player.jersey_number, 23)
        self.assertRedirects(response, self.sr.get_absolute_url())

    def test_post_invalid(self):
        self.post_data.update({'position': ''})
        response = self.client.post(self.hockeyplayer_url, data=self.post_data, follow=True)
        self.assertFormError(response, 'form', 'position', 'This field is required.')
        self.assertTemplateUsed('players/players_update.html')

# TODO add tests for other sports
