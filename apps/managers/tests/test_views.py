from django.urls import reverse

from accounts.tests import UserFactory
from divisions.tests import DivisionFactory
from ayrabo.utils.testing import BaseTestCase
from leagues.tests import LeagueFactory
from managers.forms import ManagerForm
from managers.formset_helpers import ManagerFormSetHelper
from managers.models import Manager
from managers.tests import ManagerFactory
from referees.tests import RefereeFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


class ManagersCreateViewTests(BaseTestCase):
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
            'managers-TOTAL_FORMS': 1,
            'managers-INITIAL_FORMS': 0,
            'managers-MIN_NUM_FORMS': 1,
            'managers-MAX_NUM_FORMS': 10
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
        self.sr.set_roles(['Manager'])
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_template_name(self):
        response = self.client.get(self._format_url('managers', pk=self.sr.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'managers/managers_create.html')

    def test_get_form_class(self):
        response = self.client.get(self._format_url('managers', pk=self.sr.id))
        form_cls = response.context['formset'].forms[0]
        self.assertIsInstance(form_cls, ManagerForm)

    def test_get_formset_prefix(self):
        response = self.client.get(self._format_url('managers', pk=self.sr.id))
        formset = response.context['formset']
        self.assertEqual(formset.prefix, 'managers')

    def test_get_model_class(self):
        response = self.client.get(self._format_url('managers', pk=self.sr.id))
        self.assertIs(response.context['formset'].model, Manager)

    def test_get_formset_helper_class(self):
        response = self.client.get(self._format_url('managers', pk=self.sr.id))
        self.assertIs(response.context['helper'], ManagerFormSetHelper)

    def test_get_role(self):
        response = self.client.get(self._format_url('managers', pk=self.sr.id))
        self.assertEqual(response.context['role'], 'Manager')

    def test_get_registered_for_all(self):
        self.sr.set_roles(['Manager'])
        self.sr.is_complete = True
        self.sr.save()
        ManagerFactory(user=self.user, team=self.team)
        self.sr_2.is_complete = True
        self.sr_2.save()
        response = self.client.get(self._format_url('managers', pk=self.sr.id), follow=True)
        self.assertHasMessage(response, 'You have already registered for all available teams.')
        self.assertRedirects(response, self.sr.get_absolute_url())

    # POST
    def test_post_two_forms_same_team(self):
        form_data = {
            'managers-0-team': self.team.id,
            'managers-1-team': self.team.id,
            'managers-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('managers', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 1, 'team',
                                '{} has already been selected. Please choose another team or remove this form.'.format(
                                        self.team.name))

    def test_post_already_registered_for_team(self):
        self.sr.set_roles(['Manager'])
        TeamFactory(name='My Team', division=self.division)
        ManagerFactory(user=self.user, team=self.team)
        self.sr.is_complete = True
        self.sr.save()
        ManagerFactory(user=self.user, team=self.baseball_team)
        self.sr_2.is_complete = True
        self.sr_2.save()
        form_data = {
            'managers-0-team': self.team.id,
            'managers-0-position': 'head_coach',
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('managers', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'team',
                                'Select a valid choice. That choice is not one of the available choices.')

    def test_post_one_valid_form(self):
        form_data = {
            'managers-0-team': self.team.id,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('managers', pk=self.sr.id), data=self.post_data, follow=True)
        manager = Manager.objects.filter(user=self.user, team=self.team)
        self.assertTrue(manager.exists())
        self.assertRedirects(response, self._format_url('players', pk=self.sr_2.id))
        self.assertHasMessage(response, 'You have been registered as a manager for the Green Machine IceCats.')

    def test_post_two_valid_forms(self):
        t1 = TeamFactory(division__league__sport=self.ice_hockey)
        form_data = {
            'managers-0-team': self.team.id,
            'managers-1-team': t1.id,
            'managers-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('managers', pk=self.sr.id), data=self.post_data, follow=True)
        managers = Manager.objects.filter(user=self.user)
        self.assertEqual(managers.count(), 2)
        self.assertRedirects(response, self._format_url('players', pk=self.sr_2.id))
        self.assertHasMessage(response,
                              'You have been registered as a manager for the Green Machine IceCats, {}.'.format(
                                      t1.name))

    def test_post_three_valid_forms(self):
        l1 = LeagueFactory(full_name='National Hockey League', sport=self.ice_hockey)
        l2 = LeagueFactory(sport=self.ice_hockey)
        d1 = DivisionFactory(league=l1)
        d2 = DivisionFactory(league=l2)
        t1 = TeamFactory(division=d1)
        t2 = TeamFactory(division=d2)
        form_data = {
            'managers-0-team': self.team.id,
            'managers-1-team': t1.id,
            'managers-2-team': t2.id,
            'managers-TOTAL_FORMS': 3,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('managers', pk=self.sr.id), data=self.post_data, follow=True)
        managers = Manager.objects.filter(user=self.user)
        self.assertEqual(managers.count(), 3)
        self.assertRedirects(response, self._format_url('players', pk=self.sr_2.id))
        self.assertHasMessage(response,
                              'You have been registered as a manager for the Green Machine IceCats, {}, {}.'.format(
                                      t1.name, t2.name))

    def test_post_one_invalid_form(self):
        form_data = {
            'managers-0-team': '',
            'managers-TOTAL_FORMS': 1,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('managers', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'team', 'This field is required.')

    def test_post_two_invalid_forms(self):
        form_data = {
            'managers-0-team': '',
            'managers-1-team': -1,
            'managers-TOTAL_FORMS': 2,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('managers', pk=self.sr.id), data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'team', 'This field is required.')
        self.assertFormsetError(response, 'formset', 1, 'team',
                                'Select a valid choice. That choice is not one of the available choices.')

    def test_post_empty_added_form(self):
        form_data = {
            'managers-0-team': self.team.id,
            'managers-1-team': '',
            'managers-TOTAL_FORMS': 2,
        }

        self.post_data.update(form_data)
        response = self.client.post(self._format_url('managers', pk=self.sr.id), data=self.post_data, follow=True)
        url = 'sportregistrations:{role}:create'.format(role='players')
        self.assertRedirects(response, reverse(url, kwargs={'pk': self.sr_2.id}))

    def test_next_sport_registration_fetched(self):
        self.sr.set_roles(['Manager'])
        form_data = {
            'managers-0-team': self.team.id,
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('managers', pk=self.sr.id), data=self.post_data, follow=True)
        # sr_2 has role player
        url = 'sportregistrations:{role}:create'.format(role='players')
        self.assertRedirects(response, reverse(url, kwargs={'pk': self.sr_2.id}))

    def test_no_remaining_sport_registrations(self):
        self.sr.set_roles(['Manager'])
        self.sr_2.set_roles(['Manager'])
        form_data = {
            'managers-0-team': self.team.id,
        }
        self.post_data.update(form_data)
        self.client.post(self._format_url('managers', pk=self.sr.id), data=self.post_data, follow=True)

        league = LeagueFactory(full_name='Major League Baseball', sport=self.baseball)
        division = DivisionFactory(name='American League Central', league=league)
        team = TeamFactory(name='Detroit Tigers', division=division)
        self.post_data.update({
            'managers-0-team': team.id,
        })

        response = self.client.post(self._format_url('managers', pk=self.sr_2.id), data=self.post_data, follow=True)

        self.assertRedirects(response, reverse('home'))

    def test_post_add_manager_role_valid_form(self):
        self.sr.set_roles(['Referee'])
        self.sr.is_complete = True
        self.sr.save()
        RefereeFactory(user=self.user, league=self.league)
        self.sr_2.is_complete = True
        self.sr_2.save()
        form_data = {
            'managers-0-team': self.team.id
        }
        self.post_data.update(form_data)
        response = self.client.post(self._format_url('managers', pk=self.sr.id), data=self.post_data, follow=True)
        manager = Manager.objects.filter(user=self.user, team=self.team)
        self.assertTrue(manager.exists())
        self.sr.refresh_from_db()
        self.assertTrue(self.sr.has_role('Manager'))
        self.assertHasMessage(response, 'You have been registered as a manager for the Green Machine IceCats.')

    def test_post_add_manager_role_invalid_form(self):
        self.sr.set_roles(['Referee'])
        self.sr.is_complete = True
        self.sr.save()
        RefereeFactory(user=self.user, league=self.league)
        self.sr_2.is_complete = True
        self.sr_2.save()
        form_data = {
            'managers-0-team': -1,
        }
        self.post_data.update(form_data)
        self.client.post(self._format_url('managers', pk=self.sr.id), data=self.post_data, follow=True)
        manager = Manager.objects.filter(user=self.user, team=self.team)
        self.assertFalse(manager.exists())
        self.sr.refresh_from_db()
        self.assertFalse(self.sr.has_role('Manager'))

    def test_post_registered_for_all(self):
        self.sr.set_roles(['Manager'])
        self.sr.is_complete = True
        self.sr.save()
        ManagerFactory(user=self.user, team=self.team)
        self.sr_2.is_complete = True
        self.sr_2.save()
        response = self.client.post(self._format_url('managers', pk=self.sr.id), data={}, follow=True)
        self.assertHasMessage(response, 'You have already registered for all available teams.')
        self.assertRedirects(response, self.sr.get_absolute_url())
