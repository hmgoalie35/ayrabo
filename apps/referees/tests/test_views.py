from django.urls import reverse

from accounts.tests import UserFactory
from coaches.tests import CoachFactory
from divisions.tests import DivisionFactory
from escoresheet.utils.testing_utils import BaseTestCase
from leagues.tests import LeagueFactory
from referees.forms import RefereeForm
from referees.formset_helpers import RefereeFormSetHelper
from referees.models import Referee
from referees.tests import RefereeFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


class CreateRefereesViewTests(BaseTestCase):
    def _format_url(self, role, **kwargs):
        return reverse(self.url.format(role=role), kwargs=kwargs)

    @classmethod
    def setUpClass(cls):
        super(CreateRefereesViewTests, cls).setUpClass()
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.basketball = SportFactory(name='Basketball')

    def setUp(self):
        self.url = 'sportregistrations:{role}:create'
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.post_data = {
            'referees-TOTAL_FORMS': 1,
            'referees-INITIAL_FORMS': 0,
            'referees-MIN_NUM_FORMS': 1,
            'referees-MAX_NUM_FORMS': 10
        }

        self.user = UserFactory(email=self.email, password=self.password)

        self.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.division = DivisionFactory(name='Midget Minor AA', league=self.league)

        self.baseball_league = LeagueFactory(full_name='Major League Baseball', sport=self.baseball)
        self.baseball_division = DivisionFactory(name='American League East', league=self.baseball_league)
        self.baseball_team = TeamFactory(name='New York Yankees', division=self.baseball_division)

        self.sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=False)
        self.sr_2 = SportRegistrationFactory(user=self.user, sport=self.baseball, is_complete=False)
        self.sr.set_roles(['Referee'])
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_template_name(self):
        response = self.client.get(self._format_url('referees', pk=self.sr.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'referees/referees_create.html')

    def test_get_form_class(self):
        response = self.client.get(self._format_url('referees', pk=self.sr.id))
        form_cls = response.context['formset'].forms[0]
        self.assertIsInstance(form_cls, RefereeForm)

    def test_get_formset_prefix(self):
        response = self.client.get(self._format_url('referees', pk=self.sr.id))
        formset = response.context['formset']
        self.assertEqual(formset.prefix, 'referees')

    def test_get_model_class(self):
        response = self.client.get(self._format_url('referees', pk=self.sr.id))
        self.assertIs(response.context['formset'].model, Referee)

    def test_get_formset_helper_class(self):
        response = self.client.get(self._format_url('referees', pk=self.sr.id))
        self.assertIs(response.context['helper'], RefereeFormSetHelper)

    def test_get_role(self):
        response = self.client.get(self._format_url('referees', pk=self.sr.id))
        self.assertEqual(response.context['role'], 'Referee')

    def test_get_registered_for_all(self):
        self.sr.set_roles(['Referee'])
        self.sr.is_complete = True
        self.sr.save()
        RefereeFactory(user=self.user, league=self.league)
        self.sr_2.is_complete = True
        self.sr_2.save()
        response = self.client.get(self._format_url('referees', pk=self.sr.id), follow=True)
        self.assertHasMessage(response, 'You have already registered for all available leagues.')
        self.assertRedirects(response, self.sr.get_absolute_url())

    # POST
    def test_post_two_forms_same_league(self):
        form_data = {
            'referees-0-league': self.league.id,
            'referees-1-league': self.league.id,
            'referees-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('referees', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 1, 'league', '{} has already been selected. '
                                                                  'Please choose another league or remove this form.'
                                .format(self.league.full_name))

    def test_post_already_registered_for_league(self):
        self.sr.set_roles(['Referee'])
        LeagueFactory(full_name='My League', sport=self.ice_hockey)
        RefereeFactory(user=self.user, league=self.league)
        self.sr.is_complete = True
        self.sr.save()
        RefereeFactory(user=self.user, league=self.baseball_league)
        self.sr_2.is_complete = True
        self.sr_2.save()
        form_data = {
            'referees-0-league': self.league.id,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('referees', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'league',
                                'Select a valid choice. That choice is not one of the available choices.')

    def test_post_one_valid_form(self):
        form_data = {
            'referees-0-league': self.league.id,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('referees', pk=self.sr.id), data=self.post_data, follow=True)
        manager = Referee.objects.filter(user=self.user, league=self.league)
        self.assertTrue(manager.exists())
        self.assertRedirects(response, self._format_url('players', pk=self.sr_2.id))

    def test_post_two_valid_forms(self):
        l1 = LeagueFactory(sport=self.ice_hockey)
        form_data = {
            'referees-0-league': self.league.id,
            'referees-1-league': l1.id,
            'referees-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('referees', pk=self.sr.id), data=self.post_data, follow=True)
        referees = Referee.objects.filter(user=self.user)
        self.assertEqual(referees.count(), 2)
        self.assertRedirects(response, self._format_url('players', pk=self.sr_2.id))

    def test_post_three_valid_forms(self):
        l1 = LeagueFactory(full_name='National Hockey League', sport=self.ice_hockey)
        l2 = LeagueFactory(sport=self.ice_hockey)
        form_data = {
            'referees-0-league': self.league.id,
            'referees-1-league': l1.id,
            'referees-2-league': l2.id,
            'referees-TOTAL_FORMS': 3,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('referees', pk=self.sr.id), data=self.post_data, follow=True)
        referees = Referee.objects.filter(user=self.user)
        self.assertEqual(referees.count(), 3)
        self.assertRedirects(response, self._format_url('players', pk=self.sr_2.id))

    def test_post_one_invalid_form(self):
        form_data = {
            'referees-0-league': '',
            'referees-TOTAL_FORMS': 1,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('referees', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'league', 'This field is required.')

    def test_post_two_invalid_forms(self):
        form_data = {
            'referees-0-league': '',
            'referees-1-league': -1,
            'referees-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('referees', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'league', 'This field is required.')
        self.assertFormsetError(response, 'formset', 1, 'league',
                                'Select a valid choice. That choice is not one of the available choices.')

    def test_post_empty_added_form(self):
        form_data = {
            'referees-0-league': self.league.id,
            'referees-1-league': '',
            'referees-TOTAL_FORMS': 2,
        }

        self.post_data.update(form_data)
        response = self.client.post(self._format_url('referees', pk=self.sr.id), data=self.post_data, follow=True)
        url = 'sportregistrations:{role}:create'.format(role='players')
        self.assertRedirects(response, reverse(url, kwargs={'pk': self.sr_2.id}))

    def test_next_sport_registration_fetched(self):
        self.sr.set_roles(['Referee'])
        form_data = {
            'referees-0-league': self.league.id,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('referees', pk=self.sr.id), data=self.post_data, follow=True)
        # sr_2 has role player
        url = 'sportregistrations:{role}:create'.format(role='players')
        self.assertRedirects(response, reverse(url, kwargs={'pk': self.sr_2.id}))

    def test_no_remaining_sport_registrations(self):
        self.sr.set_roles(['Referee'])
        self.sr_2.set_roles(['Referee'])
        form_data = {
            'referees-0-league': self.league.id,
        }
        self.post_data.update(form_data)
        self.client.post(self._format_url('referees', pk=self.sr.id), data=self.post_data, follow=True)

        league = LeagueFactory(full_name='Major League Baseball', sport=self.baseball)
        self.post_data.update({
            'referees-0-league': league.id,
        })

        response = self.client.post(self._format_url('referees', pk=self.sr_2.id), data=self.post_data, follow=True)

        self.assertRedirects(response, reverse('home'))

    def test_post_add_referee_role_valid_form(self):
        self.sr.set_roles(['Coach'])
        self.sr.is_complete = True
        self.sr.save()
        CoachFactory(user=self.user)
        self.sr_2.is_complete = True
        self.sr_2.save()
        form_data = {
            'referees-0-league': self.league.id
        }
        self.post_data.update(form_data)
        self.client.post(self._format_url('referees', pk=self.sr.id), data=self.post_data, follow=True)
        referee = Referee.objects.filter(user=self.user, league=self.league)
        self.assertTrue(referee.exists())
        self.sr.refresh_from_db()
        self.assertTrue(self.sr.has_role('Referee'))

    def test_post_add_referee_role_invalid_form(self):
        self.sr.set_roles(['Coach'])
        self.sr.is_complete = True
        self.sr.save()
        CoachFactory(user=self.user)
        self.sr_2.is_complete = True
        self.sr_2.save()
        form_data = {
            'referees-0-league': -1
        }
        self.post_data.update(form_data)
        self.client.post(self._format_url('referees', pk=self.sr.id), data=self.post_data, follow=True)
        referee = Referee.objects.filter(user=self.user, league=self.league)
        self.assertFalse(referee.exists())
        self.sr.refresh_from_db()
        self.assertFalse(self.sr.has_role('Referee'))

    def test_post_registered_for_all(self):
        self.sr.set_roles(['Referee'])
        self.sr.is_complete = True
        self.sr.save()
        RefereeFactory(user=self.user, league=self.league)
        self.sr_2.is_complete = True
        self.sr_2.save()
        response = self.client.post(self._format_url('referees', pk=self.sr.id), data={}, follow=True)
        self.assertHasMessage(response, 'You have already registered for all available leagues.')
        self.assertRedirects(response, self.sr.get_absolute_url())
