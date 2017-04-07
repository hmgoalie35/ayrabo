from django.urls import reverse

from accounts.tests import UserFactory
from coaches.forms import CoachForm
from coaches.formset_helpers import CoachFormSetHelper
from coaches.models import Coach
from coaches.tests import CoachFactory
from divisions.tests import DivisionFactory
from escoresheet.utils.testing_utils import BaseTestCase
from leagues.tests import LeagueFactory
from referees.tests import RefereeFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


class CreateCoachesViewTests(BaseTestCase):
    def _format_url(self, role, **kwargs):
        return reverse(self.url.format(role=role), kwargs=kwargs)

    @classmethod
    def setUpClass(cls):
        super(CreateCoachesViewTests, cls).setUpClass()
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.basketball = SportFactory(name='Basketball')

    def setUp(self):
        self.url = 'sportregistrations:{role}:create'
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.post_data = {
            'coaches-TOTAL_FORMS': 1,
            'coaches-INITIAL_FORMS': 0,
            'coaches-MIN_NUM_FORMS': 1,
            'coaches-MAX_NUM_FORMS': 10
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
        self.sr.set_roles(['Coach', 'Referee'])
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_template_name(self):
        response = self.client.get(self._format_url('coaches', pk=self.sr.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coaches/coaches_create.html')

    def test_get_form_class(self):
        response = self.client.get(self._format_url('coaches', pk=self.sr.id))
        form_cls = response.context['formset'].forms[0]
        self.assertIsInstance(form_cls, CoachForm)

    def test_get_formset_prefix(self):
        response = self.client.get(self._format_url('coaches', pk=self.sr.id))
        formset = response.context['formset']
        self.assertEqual(formset.prefix, 'coaches')

    def test_get_model_class(self):
        response = self.client.get(self._format_url('coaches', pk=self.sr.id))
        self.assertIs(response.context['formset'].model, Coach)

    def test_get_formset_helper_class(self):
        response = self.client.get(self._format_url('coaches', pk=self.sr.id))
        self.assertIs(response.context['helper'], CoachFormSetHelper)

    def test_get_role(self):
        response = self.client.get(self._format_url('coaches', pk=self.sr.id))
        self.assertEqual(response.context['role'], 'Coach')

    def test_get_registered_for_all(self):
        self.sr.set_roles(['Coach'])
        self.sr.is_complete = True
        self.sr.save()
        CoachFactory(user=self.user, team=self.team)
        self.sr_2.is_complete = True
        self.sr_2.save()
        response = self.client.get(self._format_url('coaches', pk=self.sr.id), follow=True)
        self.assertHasMessage(response, 'You have already registered for all available teams.')
        self.assertRedirects(response, self.sr.get_absolute_url())

    # POST
    def test_post_two_forms_same_team(self):
        form_data = {
            'coaches-0-team': self.team.id,
            'coaches-0-position': "Head Coach",
            'coaches-1-team': self.team.id,
            'coaches-1-position': "Assistant Coach",
            'coaches-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('coaches', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 1, 'team',
                                '{} has already been selected. Please choose another team or remove this form.'.format(
                                        self.team.name))

    def test_post_already_registered_for_team(self):
        self.sr.set_roles(['Coach'])
        TeamFactory(name='My Team', division=self.division)
        CoachFactory(user=self.user, team=self.team)
        self.sr.is_complete = True
        self.sr.save()
        CoachFactory(user=self.user, team=self.baseball_team)
        self.sr_2.is_complete = True
        self.sr_2.save()
        form_data = {
            'coaches-0-team': self.team.id,
            'coaches-0-position': 'Head Coach',
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('coaches', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'team',
                                'Select a valid choice. That choice is not one of the available choices.')

    def test_post_one_valid_form(self):
        form_data = {
            'coaches-0-team': self.team.id,
            'coaches-0-position': 'Head Coach',
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('coaches', pk=self.sr.id), data=self.post_data, follow=True)
        coach = Coach.objects.filter(user=self.user, team=self.team)
        self.assertTrue(coach.exists())
        self.assertRedirects(response, self._format_url('referees', pk=self.sr.id))

    def test_post_two_valid_forms(self):
        t1 = TeamFactory(division__league__sport=self.ice_hockey)
        form_data = {
            'coaches-0-team': self.team.id,
            'coaches-0-position': 'Head Coach',
            'coaches-1-team': t1.id,
            'coaches-1-position': 'Assistant Coach',
            'coaches-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('coaches', pk=self.sr.id), data=self.post_data, follow=True)
        coaches = Coach.objects.filter(user=self.user)
        self.assertEqual(coaches.count(), 2)
        self.assertRedirects(response, self._format_url('referees', pk=self.sr.id))

    def test_post_three_valid_forms(self):
        l1 = LeagueFactory(full_name='National Hockey League', sport=self.ice_hockey)
        l2 = LeagueFactory(sport=self.ice_hockey)
        d1 = DivisionFactory(league=l1)
        d2 = DivisionFactory(league=l2)
        t1 = TeamFactory(division=d1)
        t2 = TeamFactory(division=d2)
        form_data = {
            'coaches-0-team': self.team.id,
            'coaches-0-position': 'Head Coach',
            'coaches-1-team': t1.id,
            'coaches-1-position': 'Assistant Coach',
            'coaches-2-team': t2.id,
            'coaches-2-position': 'Assistant Coach',
            'coaches-TOTAL_FORMS': 3,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('coaches', pk=self.sr.id), data=self.post_data, follow=True)
        coaches = Coach.objects.filter(user=self.user)
        self.assertEqual(coaches.count(), 3)
        self.assertRedirects(response, self._format_url('referees', pk=self.sr.id))

    def test_post_one_invalid_form(self):
        form_data = {
            'coaches-0-position': 'Head Coach',
            'coaches-TOTAL_FORMS': 1,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('coaches', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'team', 'This field is required.')

    def test_post_two_invalid_forms(self):
        form_data = {
            'coaches-0-position': 'Head Coach',
            'coaches-1-team': self.team.id,
            'coaches-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('coaches', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'team', 'This field is required.')
        self.assertFormsetError(response, 'formset', 1, 'position', 'This field is required.')

    def test_post_empty_added_form(self):
        form_data = {
            'coaches-0-team': self.team.id,
            'coaches-0-position': 'Head Coach',
            'coaches-1-team': '',
            'coaches-1-position': '',
            'coaches-TOTAL_FORMS': 2,
        }

        # Could do an ORM call to grab the created obj, but its id is going to be 1.
        sr_id = 1

        self.post_data.update(form_data)
        response = self.client.post(self._format_url('coaches', pk=self.sr.id), data=self.post_data, follow=True)
        url = 'sportregistrations:{role}:create'.format(role='referees')
        self.assertRedirects(response, reverse(url, kwargs={'pk': sr_id}))

    def test_next_sport_registration_fetched(self):
        self.sr.set_roles(['Coach'])
        form_data = {
            'coaches-0-team': self.team.id,
            'coaches-0-position': 'Head Coach'
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('coaches', pk=self.sr.id), data=self.post_data, follow=True)
        # sr_2 has role player
        url = 'sportregistrations:{role}:create'.format(role='players')
        self.assertRedirects(response, reverse(url, kwargs={'pk': self.sr_2.id}))

    def test_no_remaining_sport_registrations(self):
        self.sr.set_roles(['Coach'])
        self.sr_2.set_roles(['Coach'])
        form_data = {
            'coaches-0-team': self.team.id,
            'coaches-0-position': 'Head Coach',
        }
        self.post_data.update(form_data)
        self.client.post(self._format_url('coaches', pk=self.sr.id), data=self.post_data, follow=True)

        league = LeagueFactory(full_name='Major League Baseball', sport=self.baseball)
        division = DivisionFactory(name='American League Central', league=league)
        team = TeamFactory(name='Detroit Tigers', division=division)
        self.post_data.update({
            'coaches-0-team': team.id,
            'coaches-0-position': 'Assistant Coach',
        })

        response = self.client.post(self._format_url('coaches', pk=self.sr_2.id), data=self.post_data, follow=True)

        self.assertRedirects(response, reverse('home'))

    def test_post_add_coach_role_valid_form(self):
        self.sr.set_roles(['Referee'])
        self.sr.is_complete = True
        self.sr.save()
        RefereeFactory(user=self.user, league=self.league)
        self.sr_2.is_complete = True
        self.sr_2.save()
        form_data = {
            'coaches-0-team': self.team.id,
            'coaches-0-position': 'Head Coach',
        }
        self.post_data.update(form_data)
        self.client.post(self._format_url('coaches', pk=self.sr.id), data=self.post_data, follow=True)
        coach = Coach.objects.filter(user=self.user, team=self.team)
        self.assertTrue(coach.exists())
        self.sr.refresh_from_db()
        self.assertTrue(self.sr.has_role('Coach'))

    def test_post_add_coach_role_invalid_form(self):
        self.sr.set_roles(['Referee'])
        self.sr.is_complete = True
        self.sr.save()
        RefereeFactory(user=self.user, league=self.league)
        self.sr_2.is_complete = True
        self.sr_2.save()
        form_data = {
            'coaches-0-team': self.team.id,
            'coaches-0-position': '',
        }
        self.post_data.update(form_data)
        self.client.post(self._format_url('coaches', pk=self.sr.id), data=self.post_data, follow=True)
        coach = Coach.objects.filter(user=self.user, team=self.team)
        self.assertFalse(coach.exists())
        self.sr.refresh_from_db()
        self.assertFalse(self.sr.has_role('Coach'))

    def test_post_registered_for_all(self):
        self.sr.set_roles(['Coach'])
        self.sr.is_complete = True
        self.sr.save()
        CoachFactory(user=self.user, team=self.team)
        self.sr_2.is_complete = True
        self.sr_2.save()
        response = self.client.post(self._format_url('coaches', pk=self.sr.id), data={}, follow=True)
        self.assertHasMessage(response, 'You have already registered for all available teams.')
        self.assertRedirects(response, self.sr.get_absolute_url())
