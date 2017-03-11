from django.urls import reverse

from accounts.tests import UserFactory
from divisions.tests import DivisionFactory
from escoresheet.utils.testing_utils import BaseTestCase
from leagues.tests import LeagueFactory
from players.models import HockeyPlayer
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


# Am testing this base view via the `CreatePlayersView`
class BaseCreateRelatedObjectsViewTests(BaseTestCase):
    def _format_url(self, role, **kwargs):
        return reverse(self.url.format(role=role), kwargs=kwargs)

    @classmethod
    def setUpClass(cls):
        super(BaseCreateRelatedObjectsViewTests, cls).setUpClass()
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

        # Could do an ORM call to grab the created obj, but its id is going to be 1.
        sr_id = 1

        self.post_data.update(form_data)
        response = self.client.post(self._format_url('players', pk=self.sr.id), data=self.post_data, follow=True)
        url = 'sportregistrations:{role}:create'.format(role='coaches')
        self.assertRedirects(response, reverse(url, kwargs={'pk': sr_id}))

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
