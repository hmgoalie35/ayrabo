import factory
from django.core import mail
from django.urls import reverse
from django.test import TestCase

from accounts.tests import UserFactory
from coaches.forms import CoachForm
from coaches.models import Coach
from coaches.tests import CoachFactory
from divisions.tests import DivisionFactory
from escoresheet.utils.testing_utils import get_messages, create_related_objects
from leagues.tests import LeagueFactory
from managers.forms import ManagerForm
from managers.models import Manager
from managers.tests import ManagerFactory
from players import forms as player_forms
from players.models import HockeyPlayer
from players.tests import HockeyPlayerFactory
from referees.forms import RefereeForm
from referees.models import Referee
from referees.tests import RefereeFactory
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory


class CreateSportRegistrationViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(CreateSportRegistrationViewTests, cls).setUpClass()
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.basketball = SportFactory(name='Basketball')

    def setUp(self):
        self.url = reverse('sport:create_sport_registration')
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.post_data = {
            'sportregistration_set-TOTAL_FORMS': 1,
            'sportregistration_set-INITIAL_FORMS': 0,
            'sportregistration_set-MIN_NUM_FORMS': 1,
            'sportregistration_set-MAX_NUM_FORMS': 3
        }

        self.user = UserFactory(email=self.email, password=self.password)
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_renders_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'sports/sport_registration_create.html')

    def test_200_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_redirects_already_registered_for_all_sports(self):
        SportRegistrationFactory(sport=self.ice_hockey, user=self.user, is_complete=True)
        SportRegistrationFactory(sport=self.baseball, user=self.user, is_complete=True)
        SportRegistrationFactory(sport=self.basketball, user=self.user, is_complete=True)
        response = self.client.get(self.url, follow=True)
        self.assertIn(
                'You have already registered for all available sports. Check back later to see if any new sports have been added.',
                get_messages(response))
        self.assertRedirects(response, reverse('home'))

    def test_form_only_displays_sports_not_registered_for(self):
        SportRegistrationFactory(sport=self.ice_hockey, user=self.user, is_complete=True)
        response = self.client.get(self.url)
        formset_as_html = response.context['formset'].as_p()
        self.assertNotIn('Ice Hockey', formset_as_html)
        self.assertIn('Basketball', formset_as_html)
        self.assertIn('Baseball', formset_as_html)

    def test_context_populated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['remaining_sport_count'], 3)
        self.assertFalse(response.context['user_registered_for_all_sports'])
        self.assertIsNotNone(response.context['formset'])

    # POST
    def test_post_anonymous_user(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.post_data, follow=True)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_post_redirects_already_registered_for_all_sports(self):
        SportRegistrationFactory(sport=self.ice_hockey, user=self.user, is_complete=True)
        SportRegistrationFactory(sport=self.baseball, user=self.user, is_complete=True)
        SportRegistrationFactory(sport=self.basketball, user=self.user, is_complete=True)
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertIn(
                'You have already registered for all available sports. Check back later to see if any new sports have been added.',
                get_messages(response))
        self.assertRedirects(response, reverse('home'))

    def test_valid_post_one_form(self):
        form_data = {
            'sportregistration_set-0-sport': self.ice_hockey.id,
            'sportregistration_set-0-roles': ['Player', 'Coach']
        }
        self.post_data.update(form_data)
        response = self.client.post(self.url, data=self.post_data, follow=True)
        sr = SportRegistration.objects.filter(user=self.user, sport=self.ice_hockey)
        self.assertTrue(sr.exists())
        self.assertEqual(sr.first().roles, ['Player', 'Coach'])
        self.assertRedirects(response, reverse('sport:finish_sport_registration'))

    def test_valid_post_two_forms(self):
        form_data = {
            'sportregistration_set-0-sport': self.ice_hockey.id,
            'sportregistration_set-0-roles': ['Player', 'Coach'],
            'sportregistration_set-1-sport': self.basketball.id,
            'sportregistration_set-1-roles': ['Player', 'Referee']
        }
        self.post_data.update(form_data)
        self.post_data['sportregistration_set-TOTAL_FORMS'] = 2

        response = self.client.post(self.url, data=self.post_data, follow=True)
        sr = SportRegistration.objects.filter(user=self.user)
        self.assertEqual(sr.count(), 2)
        self.assertEqual(sr[0].roles, ['Player', 'Coach'])
        self.assertEqual(sr[1].roles, ['Player', 'Referee'])
        self.assertRedirects(response, reverse('sport:finish_sport_registration'))

    def test_valid_post_three_forms(self):
        form_data = {
            'sportregistration_set-0-sport': self.ice_hockey.id,
            'sportregistration_set-0-roles': ['Player', 'Coach'],
            'sportregistration_set-1-sport': self.basketball.id,
            'sportregistration_set-1-roles': ['Player', 'Referee'],
            'sportregistration_set-2-sport': self.baseball.id,
            'sportregistration_set-2-roles': ['Manager', 'Referee']
        }
        self.post_data.update(form_data)
        self.post_data['sportregistration_set-TOTAL_FORMS'] = 3

        response = self.client.post(self.url, data=self.post_data, follow=True)
        sr = SportRegistration.objects.filter(user=self.user)
        self.assertEqual(sr.count(), 3)
        self.assertRedirects(response, reverse('sport:finish_sport_registration'))

    def test_post_two_forms_same_sport(self):
        form_data = {
            'sportregistration_set-0-sport': self.ice_hockey.id,
            'sportregistration_set-0-roles': ['Referee', 'Manager'],
            'sportregistration_set-1-sport': self.ice_hockey.id,
            'sportregistration_set-1-roles': ['Player', 'Coach']
        }
        self.post_data.update(form_data)
        self.post_data['sportregistration_set-TOTAL_FORMS'] = 2
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 1, 'sport',
                                'Only one form can have {sport} selected. Choose another sport, or the "---------" value.'.format(
                                        sport=self.ice_hockey))

    def test_post_one_invalid_form(self):
        form_data = {
            'sportregistration_set-0-sport': '',
        }
        self.post_data.update(form_data)
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'sport', 'This field is required.')
        self.assertFormsetError(response, 'formset', 0, 'roles', 'This field is required.')

    def test_post_two_invalid_forms(self):
        form_data = {
            'sportregistration_set-0-sport': '',
            'sportregistration_set-1-sport': '',
            'sportregistration_set-1-roles': ['Player'],
        }
        self.post_data.update(form_data)
        self.post_data['sportregistration_set-TOTAL_FORMS'] = 2
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertFormsetError(response, 'formset', 0, 'sport', 'This field is required.')
        self.assertFormsetError(response, 'formset', 1, 'sport', 'This field is required.')

    def test_post_empty_added_form(self):
        form_data = {
            'sportregistration_set-0-sport': self.ice_hockey.id,
            'sportregistration_set-0-roles': ['Player', 'Coach'],
            'sportregistration_set-1-sport': [''],
        }

        self.post_data.update(form_data)
        self.post_data['sportregistration_set-TOTAL_FORMS'] = 2
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('sport:finish_sport_registration'))


class FinishSportRegistrationViewTests(TestCase):
    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.url = reverse('sport:finish_sport_registration')

        self.coach_post_data = factory.build(dict, FACTORY_CLASS=CoachFactory)
        self.coach_post_data['coach-position'] = self.coach_post_data.pop('position')
        self.manager_post_data = factory.build(dict, FACTORY_CLASS=ManagerFactory)
        self.referee_post_data = factory.build(dict, FACTORY_CLASS=RefereeFactory)
        self.hockeyplayer_post_data = factory.build(dict, FACTORY_CLASS=HockeyPlayerFactory)

        self.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport__name='Ice Hockey')
        self.division = DivisionFactory(name='Midget Minor AA', league=self.league)
        self.team = TeamFactory(name='Green Machine IceCats', division=self.division)

        self.referee_post_data['referee-league'] = str(self.league.id)
        self.coach_post_data['coach-team'] = str(self.team.id)
        self.manager_post_data['manager-team'] = str(self.team.id)

        self.hockeyplayer_post_data['hockeyplayer-team'] = str(self.team.id)
        self.hockeyplayer_post_data['hockeyplayer-position'] = self.hockeyplayer_post_data.pop('position')
        self.hockeyplayer_post_data['hockeyplayer-jersey_number'] = self.hockeyplayer_post_data.pop('jersey_number')
        self.hockeyplayer_post_data['hockeyplayer-handedness'] = self.hockeyplayer_post_data.pop('handedness')

        del self.coach_post_data['user']
        del self.manager_post_data['user']
        del self.referee_post_data['user']
        del self.hockeyplayer_post_data['user']

        del self.coach_post_data['team']
        del self.manager_post_data['team']
        del self.referee_post_data['league']
        del self.hockeyplayer_post_data['team']
        del self.hockeyplayer_post_data['sport']

        self.user = UserFactory(email=self.email, password=self.password)
        self.sr = SportRegistrationFactory(user=self.user, sport=self.league.sport, is_complete=False)
        self.sr_2 = SportRegistrationFactory(user=self.user, sport__name='Baseball', is_complete=False)
        self.sr.set_roles(['Coach'])
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_renders_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'sports/sport_registration_finish.html')

    def test_200_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_sport_not_configured(self):
        self.sr.is_complete = True
        self.sr.save()
        self.sr_2.is_complete = True
        self.sr_2.save()
        sr = SportRegistrationFactory(user=self.user, is_complete=False)
        sr.set_roles(['Player'])
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'message.html')
        msg = "{sport} hasn't been configured correctly in our system. If you believe this is an error please contact us.".format(
                sport=sr.sport.name)
        self.assertEqual(response.context['message'], msg)
        self.assertEqual(len(mail.outbox), 1)

    def test_coach_form_in_context(self):
        """
        Only coach role
        """
        response = self.client.get(self.url)
        self.assertIn('coach_form', response.context)

    def test_manager_form_in_context(self):
        self.sr.set_roles(['Manager'])
        response = self.client.get(self.url)
        self.assertIn('manager_form', response.context)

    def test_all_forms_in_context(self):
        """
        All roles
        """
        self.sr.set_roles([role for role in SportRegistration.ROLES])
        response = self.client.get(self.url)
        self.assertIn('coach_form', response.context)
        self.assertIn('player_form', response.context)
        self.assertIn('manager_form', response.context)
        self.assertIn('referee_form', response.context)

    def test_coach_player_forms_in_context(self):
        """
        Coach and player roles
        """
        self.sr.set_roles(['Coach', 'Player'])
        response = self.client.get(self.url)
        self.assertIn('coach_form', response.context)
        self.assertIn('player_form', response.context)
        self.assertIsInstance(response.context['player_form'], player_forms.HockeyPlayerForm)

    def test_coach_manager_referee_forms_in_context(self):
        self.sr.set_roles(['Coach', 'Manager', 'Referee'])
        response = self.client.get(self.url)
        self.assertIn('coach_form', response.context)
        self.assertIn('manager_form', response.context)
        self.assertIn('referee_form', response.context)

    def test_get_account_complete(self):
        self.sr.is_complete = True
        self.sr.save()
        self.sr_2.is_complete = True
        self.sr_2.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home'))

    # it's overkill to add in tests for all permutations of SportRegistration.ROLES, but might need to do it anyway

    # POST
    def test_post_anonymous_user(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.coach_post_data, follow=True)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_post_account_complete(self):
        self.sr.is_complete = True
        self.sr.save()
        self.sr_2.is_complete = True
        self.sr_2.save()
        response = self.client.post(self.url, data=self.coach_post_data, follow=True)
        self.assertRedirects(response, reverse('home'))

    def test_post_sport_not_configured(self):
        self.sr.is_complete = True
        self.sr.save()
        self.sr_2.is_complete = True
        self.sr_2.save()
        sr = SportRegistrationFactory(user=self.user, is_complete=False)
        sr.set_roles(['Player'])
        response = self.client.post(self.url, data={}, follow=True)
        self.assertTemplateUsed(response, 'message.html')
        msg = "{sport} hasn't been configured correctly in our system. If you believe this is an error please contact us.".format(
                sport=sr.sport.name)
        self.assertEqual(response.context['message'], msg)
        self.assertEqual(len(mail.outbox), 1)

    def test_post_valid_coach_form_data(self):
        response = self.client.post(self.url, data=self.coach_post_data, follow=True)
        self.assertRedirects(response, self.url)
        self.assertTrue(Coach.objects.filter(user=self.user).exists())

    def test_post_invalid_coach_form_data(self):
        del self.coach_post_data['coach-position']
        response = self.client.post(self.url, data=self.coach_post_data, follow=True)
        self.assertFormError(response, 'coach_form', 'position', 'This field is required.')

    def test_post_valid_manager_form_data(self):
        self.sr.set_roles(['Manager'])
        response = self.client.post(self.url, data=self.manager_post_data, follow=True)

        self.assertRedirects(response, self.url)
        self.assertTrue(Manager.objects.filter(user=self.user).exists())

    def test_post_invalid_manager_form_data(self):
        self.sr.set_roles(['Manager'])
        self.manager_post_data['manager-team'] = ''
        response = self.client.post(self.url, data=self.manager_post_data, follow=True)
        self.assertFormError(response, 'manager_form', 'team', 'This field is required.')

    def test_post_valid_hockeyplayer_form_data(self):
        self.sr.set_roles(['Player'])
        response = self.client.post(self.url, data=self.hockeyplayer_post_data, follow=True)
        self.assertRedirects(response, self.url)
        self.assertTrue(HockeyPlayer.objects.filter(user=self.user).exists())

    def test_post_invalid_hockeyplayer_form_data(self):
        self.sr.set_roles(['Player'])
        self.hockeyplayer_post_data['hockeyplayer-position'] = ''
        response = self.client.post(self.url, data=self.hockeyplayer_post_data, follow=True)
        self.assertFormError(response, 'player_form', 'position', 'This field is required.')

    def test_post_valid_coach_and_manager_forms(self):
        self.sr.set_roles(['Coach', 'Manager'])
        post_data = self.manager_post_data.copy()
        post_data.update(self.coach_post_data)
        response = self.client.post(self.url, data=post_data, follow=True)
        self.assertRedirects(response, self.url)
        self.assertTrue(Manager.objects.filter(user=self.user).exists())
        self.assertTrue(Coach.objects.filter(user=self.user).exists())

    def test_post_invalid_coach_manager_forms(self):
        self.sr.set_roles(['Coach', 'Manager'])
        post_data = self.manager_post_data.copy()
        post_data.update(self.coach_post_data)
        del post_data['coach-position']
        del post_data['manager-team']
        response = self.client.post(self.url, data=post_data, follow=True)
        self.assertFormError(response, 'coach_form', 'position', 'This field is required.')
        self.assertFormError(response, 'manager_form', 'team', 'This field is required.')

    def test_post_valid_coach_manager_referee_forms(self):
        self.sr.set_roles(['Coach', 'Manager', 'Referee'])
        post_data = self.manager_post_data.copy()
        post_data.update(self.coach_post_data)
        post_data.update(self.referee_post_data)

        response = self.client.post(self.url, data=post_data, follow=True)

        self.assertRedirects(response, self.url)
        self.assertTrue(Manager.objects.filter(user=self.user).exists())
        self.assertTrue(Coach.objects.filter(user=self.user).exists())
        self.assertTrue(Referee.objects.filter(user=self.user).exists())

    def test_post_invalid_coach_manager_referee_forms(self):
        self.sr.set_roles(['Coach', 'Manager', 'Referee'])
        post_data = self.manager_post_data.copy()
        post_data.update(self.coach_post_data)
        post_data.update(self.referee_post_data)
        del post_data['coach-position']
        del post_data['manager-team']
        del post_data['referee-league']
        response = self.client.post(self.url, data=post_data, follow=True)
        self.assertFormError(response, 'coach_form', 'position', 'This field is required.')
        self.assertFormError(response, 'manager_form', 'team', 'This field is required.')
        self.assertFormError(response, 'referee_form', 'league', 'This field is required.')

    def test_post_valid_coach_manager_referee_hockeyplayer_forms(self):
        self.sr.set_roles(['Coach', 'Manager', 'Referee', 'Player'])
        post_data = self.manager_post_data.copy()
        post_data.update(self.coach_post_data)
        post_data.update(self.referee_post_data)
        post_data.update(self.hockeyplayer_post_data)

        response = self.client.post(self.url, data=post_data, follow=True)
        self.assertRedirects(response, self.url)
        self.assertTrue(Manager.objects.filter(user=self.user).exists())
        self.assertTrue(Coach.objects.filter(user=self.user).exists())
        self.assertTrue(Referee.objects.filter(user=self.user).exists())
        self.assertTrue(HockeyPlayer.objects.filter(user=self.user).exists())

    def test_post_invalid_coach_manager_referee_hockeyplayer_forms(self):
        self.sr.set_roles(['Coach', 'Manager', 'Referee', 'Player'])
        post_data = self.manager_post_data.copy()
        post_data.update(self.coach_post_data)
        post_data.update(self.referee_post_data)
        post_data.update(self.hockeyplayer_post_data)

        del post_data['coach-position']
        del post_data['manager-team']
        del post_data['referee-league']
        del post_data['hockeyplayer-position']

        response = self.client.post(self.url, data=post_data, follow=True)
        self.assertFormError(response, 'coach_form', 'position', 'This field is required.')
        self.assertFormError(response, 'manager_form', 'team', 'This field is required.')
        self.assertFormError(response, 'referee_form', 'league', 'This field is required.')
        self.assertFormError(response, 'player_form', 'position', 'This field is required.')

    def test_post_invalid_coach_form_valid_manager_form(self):
        """
        We only want to save the forms if all of the submitted forms are valid
        """
        self.sr.set_roles(['Coach', 'Manager'])
        post_data = self.manager_post_data.copy()
        post_data.update(self.coach_post_data)
        # Coach form is invalid
        del post_data['coach-position']
        response = self.client.post(self.url, data=post_data, follow=True)
        self.assertFormError(response, 'coach_form', 'position', 'This field is required.')
        self.assertFalse(Manager.objects.filter(user=self.user).exists())
        self.assertFalse(Coach.objects.filter(user=self.user).exists())

    def test_next_sport_registration_fetched(self):
        response = self.client.post(self.url, data=self.coach_post_data, follow=True)
        self.assertTrue(response.context['sport_registrations_exist'])
        self.assertRedirects(response, self.url)
        self.assertTrue(SportRegistration.objects.get(user=self.user, sport=self.sr.sport).is_complete)


class UpdateSportRegistrationViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(UpdateSportRegistrationViewTests, cls).setUpClass()
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.division = DivisionFactory(name='Midget Minor AA', league=cls.league)
        cls.team = TeamFactory(name='Green Machine Icecats', division=cls.division)

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.post_data = None
        self.user = UserFactory(email=self.email, password=self.password)
        self.sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True, roles_mask=15)
        self.url = reverse('sport:update_sport_registration', kwargs={'pk': self.sr.pk})
        self.sr_2 = SportRegistrationFactory(user=self.user, sport=self.baseball, is_complete=True, roles_mask=15)

        self.coach_post_data = {'user': self.user, 'team': self.team, 'position': 'Head Coach'}
        self.player_post_data = {'user': self.user, 'team': self.team, 'jersey_number': 23, 'handedness': 'Right',
                                 'position': 'G', 'sport': self.ice_hockey}
        self.referee_post_data = {'user': self.user, 'league': self.league}
        self.manager_post_data = {'user': self.user, 'team': self.team}

        self.player, self.coach, self.referee, self.manager = create_related_objects(
                player_args=self.player_post_data,
                coach_args=self.coach_post_data,
                referee_args=self.referee_post_data,
                manager_args=self.manager_post_data)

        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_get_not_object_owner(self):
        self.client.logout()
        other_user = UserFactory(email='otheruser@example.com', password=self.password)
        SportRegistrationFactory(user=other_user, sport=self.ice_hockey, is_complete=True)
        self.client.login(email=other_user.email, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_renders_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'sports/sport_registration_update.html')

    def test_200_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_invalid_obj_id(self):
        response = self.client.get(reverse('sport:update_sport_registration', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_role_forms_instantiated(self):
        response = self.client.get(self.url)
        self.assertIsNotNone(response.context['player_form'])
        self.assertIsNotNone(response.context['coach_form'])
        self.assertIsNotNone(response.context['referee_form'])
        self.assertIsNotNone(response.context['manager_form'])

    def test_get_sport_not_configured(self):
        sr = SportRegistrationFactory(user=self.user)
        sr.set_roles(['Player'])
        response = self.client.get(reverse('sport:update_sport_registration', kwargs={'pk': sr.pk}))
        self.assertTemplateUsed(response, 'message.html')
        msg = "{sport} hasn't been configured correctly in our system. If you believe this is an error please contact us.".format(
                sport=sr.sport.name)
        self.assertEqual(response.context['message'], msg)
        self.assertEqual(len(mail.outbox), 1)

    # POST
    def test_post_anonymous_user(self):
        self.client.logout()
        response = self.client.post(self.url, data={}, follow=True)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_post_not_object_owner(self):
        self.client.logout()
        other_user = UserFactory(email='otheruser@example.com', password=self.password)
        SportRegistrationFactory(user=other_user, sport=self.ice_hockey, is_complete=True)
        self.client.login(email=other_user.email, password=self.password)
        response = self.client.post(self.url, data={}, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_post_sport_not_configured(self):
        sr = SportRegistrationFactory(user=self.user)
        sr.set_roles(['Player'])
        response = self.client.post(reverse('sport:update_sport_registration', kwargs={'pk': sr.pk}), data={},
                                    follow=True)
        self.assertTemplateUsed(response, 'message.html')
        msg = "{sport} hasn't been configured correctly in our system. If you believe this is an error please contact us.".format(
                sport=sr.sport.name)
        self.assertEqual(response.context['message'], msg)
        self.assertEqual(len(mail.outbox), 1)

    def test_post_changed_forms(self):
        del self.coach_post_data['user']
        del self.player_post_data['user']
        del self.referee_post_data['user']
        del self.manager_post_data['user']

        del self.player_post_data['jersey_number']
        del self.coach_post_data['position']

        self.coach_post_data['coach-team'] = self.coach_post_data.pop('team').id
        self.coach_post_data['coach-position'] = 'Assistant Coach'
        self.referee_post_data['referee-league'] = str(self.referee_post_data.pop('league').id)
        self.manager_post_data['manager-team'] = str(self.manager_post_data.pop('team').id)

        self.player_post_data['hockeyplayer-team'] = str(self.player_post_data.pop('team').id)
        self.player_post_data['hockeyplayer-position'] = self.player_post_data.pop('position')
        self.player_post_data['hockeyplayer-jersey_number'] = 55
        self.player_post_data['hockeyplayer-handedness'] = self.player_post_data.pop('handedness')

        post_data = {}
        post_data.update(self.coach_post_data)
        post_data.update(self.referee_post_data)
        post_data.update(self.manager_post_data)
        post_data.update(self.player_post_data)

        response = self.client.post(self.url, data=post_data, follow=True)

        self.assertRedirects(response, reverse('account_home'))
        self.assertIn('Sport registration for {sport} successfully updated.'.format(sport=self.ice_hockey.name),
                      get_messages(response))

    def test_post_unchanged_forms(self):
        del self.coach_post_data['user']
        del self.player_post_data['user']
        del self.referee_post_data['user']
        del self.manager_post_data['user']

        self.coach_post_data['coach-team'] = self.coach_post_data.pop('team').id
        self.coach_post_data['coach-position'] = self.coach_post_data.pop('position')
        self.referee_post_data['referee-league'] = self.referee_post_data.pop('league').id
        self.manager_post_data['manager-team'] = self.manager_post_data.pop('team').id

        self.player_post_data['hockeyplayer-team'] = self.player_post_data.pop('team').id
        self.player_post_data['hockeyplayer-position'] = self.player_post_data.pop('position')
        self.player_post_data['hockeyplayer-jersey_number'] = self.player_post_data.pop('jersey_number')
        self.player_post_data['hockeyplayer-handedness'] = self.player_post_data.pop('handedness')

        post_data = {}
        post_data.update(self.coach_post_data)
        post_data.update(self.referee_post_data)
        post_data.update(self.manager_post_data)
        post_data.update(self.player_post_data)

        response = self.client.post(self.url, data=post_data, follow=True)

        self.assertTemplateUsed(response, 'sports/sport_registration_update.html')


class AddSportRegistrationRoleViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(AddSportRegistrationRoleViewTests, cls).setUpClass()
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')
        cls.league = LeagueFactory(full_name='Long Island Amateur Hockey League', sport=cls.ice_hockey)
        cls.division = DivisionFactory(name='Midget Minor AA', league=cls.league)
        cls.team = TeamFactory(name='Green Machine Icecats', division=cls.division)

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.post_data = None
        self.user = UserFactory(email=self.email, password=self.password)
        self.sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True, roles_mask=0)

        self.coach_post_data = factory.build(dict, FACTORY_CLASS=CoachFactory)
        self.coach_post_data['coach-position'] = self.coach_post_data.pop('position')
        self.manager_post_data = factory.build(dict, FACTORY_CLASS=ManagerFactory)
        self.referee_post_data = factory.build(dict, FACTORY_CLASS=RefereeFactory)
        self.hockeyplayer_post_data = factory.build(dict, FACTORY_CLASS=HockeyPlayerFactory)
        self.referee_post_data['referee-league'] = str(self.league.id)
        self.coach_post_data['coach-team'] = str(self.team.id)
        self.manager_post_data['manager-team'] = str(self.team.id)

        self.hockeyplayer_post_data['hockeyplayer-team'] = str(self.team.id)
        self.hockeyplayer_post_data['hockeyplayer-position'] = self.hockeyplayer_post_data.pop('position')
        self.hockeyplayer_post_data['hockeyplayer-jersey_number'] = self.hockeyplayer_post_data.pop('jersey_number')
        self.hockeyplayer_post_data['hockeyplayer-handedness'] = self.hockeyplayer_post_data.pop('handedness')

        del self.coach_post_data['user']
        del self.manager_post_data['user']
        del self.referee_post_data['user']
        del self.hockeyplayer_post_data['user']

        del self.coach_post_data['team']
        del self.manager_post_data['team']
        del self.referee_post_data['league']
        del self.hockeyplayer_post_data['team']
        del self.hockeyplayer_post_data['sport']

        self.client.login(email=self.email, password=self.password)

    # as a user who does not already have player, coach, etc. objects.
    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        url = reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'player'})
        response = self.client.get(url)
        result_url = '%s?next=%s' % (reverse('account_login'), url)
        self.assertRedirects(response, result_url)

    def test_get_player_role(self):
        response = self.client.get(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'player'}))

        self.assertIsInstance(response.context['form'], player_forms.HockeyPlayerForm)
        self.assertEqual(response.context['role'], 'player')
        self.assertEqual(response.context['sport_registration'].id, self.sr.id)
        self.assertTemplateUsed(response, 'sports/sport_registration_add_role.html')

    def test_get_coach_role(self):
        response = self.client.get(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'coach'}))

        self.assertIsInstance(response.context['form'], CoachForm)
        self.assertEqual(response.context['role'], 'coach')
        self.assertEqual(response.context['sport_registration'].id, self.sr.id)

    def test_get_referee_role(self):
        response = self.client.get(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'referee'}))

        self.assertIsInstance(response.context['form'], RefereeForm)
        self.assertEqual(response.context['role'], 'referee')
        self.assertEqual(response.context['sport_registration'].id, self.sr.id)

    def test_get_manager_role(self):
        response = self.client.get(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'manager'}))

        self.assertIsInstance(response.context['form'], ManagerForm)
        self.assertEqual(response.context['role'], 'manager')
        self.assertEqual(response.context['sport_registration'].id, self.sr.id)

    def test_get_not_object_owner(self):
        other_user = UserFactory(email='otheruser@example.com', password=self.password)
        sr = SportRegistrationFactory(user=other_user, sport=self.ice_hockey)

        response = self.client.get(
                reverse('sport:add_sport_registration_role', kwargs={'pk': sr.pk, 'role': 'manager'}))

        self.assertEqual(response.status_code, 404)

    def test_get_when_sport_registration_already_has_role(self):
        self.sr.set_roles(['Manager'])
        response = self.client.get(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'manager'}), follow=True)

        self.assertRedirects(response, self.sr.get_absolute_url())
        self.assertIn('You are already registered as a manager.', get_messages(response))

    # POST
    def test_post_anonymous_user(self):
        self.client.logout()
        url = reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'player'})
        response = self.client.post(url, data={}, follow=True)
        result_url = '%s?next=%s' % (reverse('account_login'), url)
        self.assertRedirects(response, result_url)

    def test_post_not_object_owner(self):
        other_user = UserFactory(email='otheruser@example.com', password=self.password)
        sr = SportRegistrationFactory(user=other_user, sport=self.ice_hockey)

        response = self.client.post(
                reverse('sport:add_sport_registration_role', kwargs={'pk': sr.pk, 'role': 'manager'}),
                data=self.manager_post_data, follow=True)

        self.assertEqual(response.status_code, 404)

    def test_post_when_sport_registration_already_has_role(self):
        self.sr.set_roles(['Manager'])
        response = self.client.post(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'manager'}),
                data=self.manager_post_data, follow=True)
        self.assertRedirects(response, self.sr.get_absolute_url())
        self.assertIn('You are already registered as a manager.', get_messages(response))

    def test_post_player_valid_data(self):
        self.assertNotIn('Player', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)
        response = self.client.post(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'player'}),
                data=self.hockeyplayer_post_data, follow=True)
        self.assertRedirects(response, self.sr.get_absolute_url())
        self.assertIn('Player role successfully added to Ice Hockey', get_messages(response))
        self.assertTrue(HockeyPlayer.objects.filter(user=self.user, team=self.team).exists())
        self.assertIn('Player', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)

    def test_post_coach_valid_data(self):
        self.assertNotIn('Coach', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)
        response = self.client.post(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'coach'}),
                data=self.coach_post_data, follow=True)
        self.assertRedirects(response, self.sr.get_absolute_url())
        self.assertIn('Coach role successfully added to Ice Hockey', get_messages(response))
        self.assertTrue(Coach.objects.filter(user=self.user, team=self.team).exists())
        self.assertIn('Coach', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)

    def test_post_referee_valid_data(self):
        self.assertNotIn('Referee', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)
        response = self.client.post(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'referee'}),
                data=self.referee_post_data, follow=True)
        self.assertRedirects(response, self.sr.get_absolute_url())
        self.assertIn('Referee role successfully added to Ice Hockey', get_messages(response))
        self.assertTrue(Referee.objects.filter(user=self.user, league=self.league).exists())
        self.assertIn('Referee', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)

    def test_post_manager_valid_data(self):
        self.assertNotIn('Manager', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)
        response = self.client.post(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'manager'}),
                data=self.manager_post_data, follow=True)
        self.assertRedirects(response, self.sr.get_absolute_url())
        self.assertIn('Manager role successfully added to Ice Hockey', get_messages(response))
        self.assertTrue(Manager.objects.filter(user=self.user, team=self.team).exists())
        self.assertIn('Manager', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)

    def test_post_invalid_data(self):
        del self.hockeyplayer_post_data['hockeyplayer-handedness']
        self.sr.set_roles(['Coach'])
        self.assertNotIn('Player', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)
        response = self.client.post(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'player'}),
                data=self.hockeyplayer_post_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sports/sport_registration_add_role.html')
        self.assertNotIn('Player role successfully added to Ice Hockey', get_messages(response))
        self.assertFalse(HockeyPlayer.objects.filter(user=self.user, team=self.team).exists())
        self.assertNotIn('Player', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)

    # as a user who already has player, coach, etc. objects. (the user unregistered for a role
    # and then re-registered for the role)
    # GET
    def test_get_player_obj_exists(self):
        player_data = {'user': self.user, 'team': self.team, 'jersey_number': 23, 'handedness': 'Right',
                       'position': 'G', 'sport': self.ice_hockey}
        player, _, _, _ = create_related_objects(player_args=player_data)
        response = self.client.get(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'player'}))
        self.assertIsNotNone(response.context['related_role_object'])
        self.assertEqual(response.context['form'].instance.id, player.id)

    def test_get_coach_obj_exists(self):
        coach_data = {'user': self.user, 'team': self.team, 'position': 'Head Coach'}
        _, coach, _, _ = create_related_objects(coach_args=coach_data)
        response = self.client.get(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'coach'}))
        self.assertIsNotNone(response.context['related_role_object'])
        self.assertEqual(response.context['form'].instance.id, coach.id)

    def test_get_referee_obj_exists(self):
        referee_data = {'user': self.user, 'league': self.league}
        _, _, referee, _ = create_related_objects(referee_args=referee_data)
        response = self.client.get(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'referee'}))
        self.assertIsNotNone(response.context['related_role_object'])
        self.assertEqual(response.context['form'].instance.id, referee.id)

    def test_get_manager_obj_exists(self):
        manager_data = {'user': self.user, 'team': self.team}
        _, _, _, manager = create_related_objects(manager_args=manager_data)
        response = self.client.get(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'manager'}))
        self.assertIsNotNone(response.context['related_role_object'])
        self.assertEqual(response.context['form'].instance.id, manager.id)

    # POST
    def test_post_player_obj_exists(self):
        player_data = {'user': self.user, 'team': self.team, 'jersey_number': 23, 'handedness': 'Right',
                       'position': 'G', 'sport': self.ice_hockey}
        player, _, _, _ = create_related_objects(player_args=player_data)

        del player_data['user']
        player_data['hockeyplayer-team'] = player_data.pop('team').id
        player_data['hockeyplayer-position'] = player_data.pop('position')
        player_data['hockeyplayer-jersey_number'] = player_data.pop('jersey_number')
        player_data['hockeyplayer-handedness'] = player_data.pop('handedness')

        response = self.client.post(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'player'}),
                data=player_data, follow=True)

        self.assertRedirects(response, self.sr.get_absolute_url())
        self.assertIn('Player', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)
        self.assertIn('{role} role successfully added to {sport}'.format(role='Player', sport=self.ice_hockey),
                      get_messages(response))

    def test_post_coach_obj_exists(self):
        coach_data = {'user': self.user, 'team': self.team, 'position': 'Head Coach'}
        _, coach, _, _ = create_related_objects(coach_args=coach_data)

        del coach_data['user']
        coach_data['coach-team'] = coach_data.pop('team').id
        coach_data['coach-position'] = coach_data.pop('position')

        response = self.client.post(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'coach'}),
                data=coach_data, follow=True)

        self.assertRedirects(response, self.sr.get_absolute_url())
        self.assertIn('Coach', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)
        self.assertIn('{role} role successfully added to {sport}'.format(role='Coach', sport=self.ice_hockey),
                      get_messages(response))

    def test_post_referee_obj_exists(self):
        referee_data = {'user': self.user, 'league': self.league}
        _, _, referee, _ = create_related_objects(referee_args=referee_data)

        del referee_data['user']
        referee_data['referee-league'] = referee_data.pop('league').id

        response = self.client.post(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'referee'}),
                data=referee_data, follow=True)

        self.assertRedirects(response, self.sr.get_absolute_url())
        self.assertIn('Referee', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)
        self.assertIn('{role} role successfully added to {sport}'.format(role='Referee', sport=self.ice_hockey),
                      get_messages(response))

    def test_post_manager_obj_exists(self):
        manager_data = {'user': self.user, 'team': self.team}
        _, _, _, manager = create_related_objects(manager_args=manager_data)

        del manager_data['user']
        manager_data['manager-team'] = manager_data.pop('team').id

        response = self.client.post(
                reverse('sport:add_sport_registration_role', kwargs={'pk': self.sr.pk, 'role': 'manager'}),
                data=manager_data, follow=True)

        self.assertRedirects(response, self.sr.get_absolute_url())
        self.assertIn('Manager', SportRegistration.objects.get(user=self.user, sport=self.sr.sport).roles)
        self.assertIn('{role} role successfully added to {sport}'.format(role='Manager', sport=self.ice_hockey),
                      get_messages(response))
