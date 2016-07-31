import factory
from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.tests.factories.UserFactory import UserFactory
from coaches.models import Coach
from coaches.tests.factories.CoachFactory import CoachFactory
from divisions.tests.factories.DivisionFactory import DivisionFactory
from escoresheet.testing_utils import get_messages
from leagues.tests.factories.LeagueFactory import LeagueFactory
from managers.models import Manager
from managers.tests.factories.ManagerFactory import ManagerFactory
from players.forms import HockeyPlayerForm
from players.models import HockeyPlayer
from players.tests.factories.PlayerFactory import HockeyPlayerFactory
from referees.models import Referee
from referees.tests.factories.RefereeFactory import RefereeFactory
from sports.tests.factories.SportFactory import SportFactory
from teams.tests.factories.TeamFactory import TeamFactory
from userprofiles.models import UserProfile, RolesMask
from .factories.RolesMaskFactory import RolesMaskFactory
from .factories.UserProfileFactory import UserProfileFactory


class CreateUserProfileViewTests(TestCase):
    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.soccer = SportFactory(name='Soccer')
        self.post_data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        self.post_data.update({'sports': [str(self.ice_hockey.id), str(self.soccer.id)]})
        self.user = UserFactory.create(email=self.email, password=self.password, userprofile=None)
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse('profile:create'))
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('profile:create'))
        self.assertRedirects(response, result_url)

    def test_correct_template(self):
        response = self.client.get(reverse('profile:create'))
        self.assertTemplateUsed(response, 'userprofiles/create.html')

    def test_200_status_code(self):
        response = self.client.get(reverse('profile:create'))
        self.assertEqual(response.status_code, 200)

    def test_form_in_context(self):
        response = self.client.get(reverse('profile:create'))
        self.assertIsNotNone(response.context['form'])

    def test_get_userprofile_already_created(self):
        self.client.logout()
        user_with_profile = UserFactory.create(password=self.password)
        RolesMaskFactory(user=user_with_profile, are_roles_set=False, are_role_objects_created=False)
        self.client.login(email=user_with_profile.email, password=self.password)
        response = self.client.get(reverse('profile:create'))
        self.assertRedirects(response, reverse('profile:select_roles'))

    # POST
    def test_post_anonymous_user(self):
        self.client.logout()
        response = self.client.post(reverse('profile:create'), data=self.post_data)
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('profile:create'))
        self.assertRedirects(response, result_url)

    def test_post_userprofile_already_created(self):
        self.client.logout()
        user_with_profile = UserFactory.create(password=self.password)
        RolesMaskFactory(user=user_with_profile, are_roles_set=False, are_role_objects_created=False)
        self.client.login(email=user_with_profile.email, password=self.password)
        response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('profile:select_roles'))

    def test_valid_post_data(self):
        response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('profile:select_roles'))

    def test_user_attribute_is_set(self):
        self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_roles_mask_objects_created(self):
        """
        This tests that POSTing sport ids will result in the appropriate RolesMask objects being created for that sport
        and user
        """
        self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        hockey_roles_mask = RolesMask.objects.filter(user=self.user, sport=self.ice_hockey)
        soccer_roles_mask = RolesMask.objects.filter(user=self.user, sport=self.soccer)

        self.assertTrue(hockey_roles_mask.exists())
        self.assertTrue(soccer_roles_mask.exists())

    # Invalid POST data
    def test_post_invalid_sport_id(self):
        self.post_data['sports'] = ['1000']
        self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertQuerysetEqual(RolesMask.objects.all(), [])

    def test_no_height_weight_gender(self):
        self.post_data.pop('gender')
        self.post_data.pop('height')
        self.post_data.pop('weight')
        response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertFormError(response, 'form', 'gender', 'This field is required.')
        self.assertFormError(response, 'form', 'height', 'This field is required.')
        self.assertFormError(response, 'form', 'weight', 'This field is required.')

    def test_invalid_height_format(self):
        invalid_heights = ['5 7', '5 7\"', '5\' 7']
        for invalid_height in invalid_heights:
            self.post_data['height'] = invalid_height
            response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
            self.assertFormError(response, 'form', 'height', 'Invalid format, please use the following format: 5\' 7"')

    def test_negative_and_zero_weights(self):
        invalid_weights = [-1, -100, 0]
        for invalid_weight in invalid_weights:
            self.post_data['weight'] = invalid_weight
            response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
            self.assertFormError(response, 'form', 'weight', 'Ensure this value is greater than or equal to 1.')

    def test_decimal_weights(self):
        invalid_weights = [.5, -.5]
        for invalid_weight in invalid_weights:
            self.post_data['weight'] = invalid_weight
            response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
            self.assertFormError(response, 'form', 'weight', 'Enter a whole number.')

    def test_no_sports(self):
        self.post_data['sports'] = []
        response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertFormError(response, 'form', 'sports', 'This field is required.')


class UpdateUserProfileViewTests(TestCase):
    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'

        self.post_data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        del self.post_data['roles_mask']
        self.post_data['roles'] = ['Player']

        self.user = UserFactory.create(email=self.email, password=self.password)
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse('profile:update'))
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('profile:update'))
        self.assertRedirects(response, result_url)

    def test_correct_template(self):
        response = self.client.get(reverse('profile:update'))
        self.assertTemplateUsed(response, 'userprofiles/update.html')

    def test_200_status_code(self):
        response = self.client.get(reverse('profile:update'))
        self.assertEqual(response.status_code, 200)

    def test_roles_in_context(self):
        response = self.client.get(reverse('profile:update'))
        self.assertIn('user_roles', response.context)

    # POST
    # No need to test invalid values for height, weight, etc. That is done above (the forms are almost identical)
    def test_post_anonymous_user(self):
        self.client.logout()
        self.post_data.pop('gender')
        self.post_data.pop('birthday')
        response = self.client.post(reverse('profile:update'), data=self.post_data, follow=True)
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('profile:update'))
        self.assertRedirects(response, result_url)

    def test_post_no_changed_data(self):
        self.post_data.pop('gender')
        self.post_data.pop('birthday')
        response = self.client.post(reverse('profile:update'), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('profile:update'))

    def test_post_changed_data(self):
        # calling the factory will generate random values for all fields
        self.post_data.pop('gender')
        self.post_data.pop('birthday')
        response = self.client.post(reverse('profile:update'), data=self.post_data, follow=True)
        success_msg = 'Your profile has been updated'
        self.assertIn(success_msg, get_messages(response))
        self.assertTemplateUsed('userprofiles/update.html')

    def test_userprofile_exists_in_context(self):
        self.post_data.pop('gender')
        self.post_data.pop('birthday')
        response = self.client.post(reverse('profile:update'), data=self.post_data, follow=True)
        self.assertIn('userprofile', response.context)


class SelectRolesViewTests(TestCase):
    def setUp(self):
        self.url = reverse('profile:select_roles')
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory.create(email=self.email, password=self.password)
        self.user.userprofile.is_complete = False
        self.ice_hockey_rm = RolesMaskFactory(user=self.user, sport__name='Ice Hockey', are_role_objects_created=False,
                                              are_roles_set=False, roles_mask=0)
        self.soccer_rm = RolesMaskFactory(user=self.user, sport__name='Soccer', are_role_objects_created=False,
                                          are_roles_set=False, roles_mask=0)
        self.tennis_rm = RolesMaskFactory(user=self.user, sport__name='Tennis', are_role_objects_created=False,
                                          are_roles_set=False, roles_mask=0)

        self.roles = ['Player', 'Coach', 'Manager']
        self.post_data = {'roles': self.roles}

        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    def test_renders_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'userprofiles/select_roles.html')

    def test_200_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_all_incomplete_roles_masks_exist(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['remaining_roles_masks'], 3)
        self.assertTrue(response.context['incomplete_roles_masks_exist'])
        self.assertEqual(response.context['sport_name'], 'Ice Hockey')
        self.assertIsNotNone(response.context['form'])

    def test_get_2_incomplete_roles_masks_exist(self):
        self.ice_hockey_rm.are_roles_set = True
        self.ice_hockey_rm.save()
        response = self.client.get(self.url)
        self.assertEqual(response.context['remaining_roles_masks'], 2)
        self.assertTrue(response.context['incomplete_roles_masks_exist'])
        self.assertEqual(response.context['sport_name'], 'Soccer')
        self.assertIsNotNone(response.context['form'])

    def test_get_1_incomplete_roles_masks_exist(self):
        self.ice_hockey_rm.are_roles_set = True
        self.ice_hockey_rm.save()
        self.soccer_rm.are_roles_set = True
        self.soccer_rm.save()
        response = self.client.get(self.url)
        self.assertEqual(response.context['remaining_roles_masks'], 1)
        self.assertTrue(response.context['incomplete_roles_masks_exist'])
        self.assertEqual(response.context['sport_name'], 'Tennis')
        self.assertIsNotNone(response.context['form'])

    def test_get_no_incomplete_roles_masks_exist_redirects(self):
        self.ice_hockey_rm.are_roles_set = True
        self.ice_hockey_rm.save()
        self.soccer_rm.are_roles_set = True
        self.soccer_rm.save()
        self.tennis_rm.are_roles_set = True
        self.tennis_rm.save()
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('profile:finish'))

    # POST
    def test_post_anonymous_user(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.post_data, follow=True)
        result_url = '%s?next=%s' % (reverse('account_login'), self.url)
        self.assertRedirects(response, result_url)

    # Valid POST data
    def test_post_all_incomplete_roles_masks_exist(self):
        response = self.client.post(self.url, data=self.post_data, follow=True)
        # We POSTed valid data, so the response should now have 1 less remaining role mask, and the next sport should
        # be in the context
        self.assertEqual(response.context['remaining_roles_masks'], 2)
        self.assertTrue(response.context['incomplete_roles_masks_exist'])
        self.assertEqual(response.context['sport_name'], 'Soccer')
        self.assertIsNotNone(response.context['form'])
        self.assertRedirects(response, self.url)

    def test_post_2_incomplete_roles_masks_exist(self):
        self.ice_hockey_rm.are_roles_set = True
        self.ice_hockey_rm.save()
        response = self.client.post(self.url, data=self.post_data, follow=True)
        # We POSTed valid data, so the response should now have 1 less remaining role mask, and the next sport should
        # be in the context
        self.assertEqual(response.context['remaining_roles_masks'], 1)
        self.assertTrue(response.context['incomplete_roles_masks_exist'])
        self.assertEqual(response.context['sport_name'], 'Tennis')
        self.assertIsNotNone(response.context['form'])
        self.assertRedirects(response, self.url)

    def test_post_1_incomplete_roles_masks_exist(self):
        self.ice_hockey_rm.are_roles_set = True
        self.ice_hockey_rm.save()
        self.soccer_rm.are_roles_set = True
        self.soccer_rm.save()
        response = self.client.post(self.url, data=self.post_data, follow=True)
        # We POSTed valid data, when there was only 1 more remaining roles mask left, so we should redirect
        # to profile finish page
        self.assertRedirects(response, reverse('profile:finish'))

    def test_post_no_incomplete_roles_masks_exist_redirects(self):
        self.ice_hockey_rm.are_roles_set = True
        self.ice_hockey_rm.save()
        self.soccer_rm.are_roles_set = True
        self.soccer_rm.save()
        self.tennis_rm.are_roles_set = True
        self.tennis_rm.save()
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('profile:finish'))

    def test_post_updates_roles_and_are_roles_set(self):
        self.client.post(self.url, data=self.post_data, follow=True)
        rm = RolesMask.objects.get(user=self.user, sport__name='Ice Hockey')
        self.assertEqual(rm.roles, self.roles)
        self.assertTrue(rm.are_roles_set)

    # Invalid POST data
    def test_post_invalid_role(self):
        self.post_data['roles'] = ['InvalidChoice']
        response = self.client.post(self.url, data=self.post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userprofiles/select_roles.html')
        self.assertFormError(response, 'form', 'roles',
                             'Select a valid choice. InvalidChoice is not one of the available choices.')


class FinishUserProfileViewTests(TestCase):
    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'

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
        self.rm = RolesMaskFactory(user=self.user, sport=self.league.sport, are_roles_set=True,
                                   are_role_objects_created=False)
        self.rm_2 = RolesMaskFactory(user=self.user, sport__name='Baseball', are_roles_set=True,
                                     are_role_objects_created=False)
        self.rm.set_roles(['Coach'])
        self.client.login(email=self.email, password=self.password)

        self.url = reverse('profile:finish')

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('profile:finish'))
        self.assertRedirects(response, result_url)

    def test_renders_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'userprofiles/finish_profile.html')

    def test_200_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_coach_form_in_context(self):
        """
        Only coach role
        """
        response = self.client.get(self.url)
        self.assertIn('coach_form', response.context)

    def test_manager_form_in_context(self):
        self.rm.set_roles(['Manager'])
        response = self.client.get(self.url)
        self.assertIn('manager_form', response.context)

    def test_all_forms_in_context(self):
        """
        All roles
        """
        self.rm.set_roles([role for role in UserProfile.ROLES])
        response = self.client.get(self.url)
        self.assertIn('coach_form', response.context)
        self.assertIn('player_form', response.context)
        self.assertIn('manager_form', response.context)
        self.assertIn('referee_form', response.context)

    def test_coach_player_forms_in_context(self):
        """
        Coach and player roles
        """
        self.rm.set_roles(['Coach', 'Player'])
        response = self.client.get(self.url)
        self.assertIn('coach_form', response.context)
        self.assertIn('player_form', response.context)
        self.assertIsInstance(response.context['player_form'], HockeyPlayerForm)

    def test_coach_manager_referee_forms_in_context(self):
        self.rm.set_roles(['Coach', 'Manager', 'Referee'])
        response = self.client.get(self.url)
        self.assertIn('coach_form', response.context)
        self.assertIn('manager_form', response.context)
        self.assertIn('referee_form', response.context)

    def test_get_account_complete(self):
        self.rm.are_role_objects_created = True
        self.rm.save()
        self.rm_2.are_role_objects_created = True
        self.rm_2.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home'))

    # it's overkill to add in tests for all permutations of RolesMask.ROLES, but might need to do it anyway

    # POST
    def test_post_anonymous_user(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.coach_post_data, follow=True)
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('profile:finish'))
        self.assertRedirects(response, result_url)

    def test_post_account_complete(self):
        self.rm.are_role_objects_created = True
        self.rm.save()
        self.rm_2.are_role_objects_created = True
        self.rm_2.save()
        response = self.client.post(self.url, data=self.coach_post_data, follow=True)
        self.assertRedirects(response, reverse('home'))

    def test_post_valid_coach_form_data(self):
        response = self.client.post(self.url, data=self.coach_post_data, follow=True)
        self.assertRedirects(response, self.url)
        self.assertTrue(Coach.objects.filter(user=self.user).exists())

    def test_post_invalid_coach_form_data(self):
        del self.coach_post_data['coach-position']
        response = self.client.post(self.url, data=self.coach_post_data, follow=True)
        self.assertFormError(response, 'coach_form', 'position', 'This field is required.')

    def test_post_valid_manager_form_data(self):
        self.rm.set_roles(['Manager'])
        response = self.client.post(self.url, data=self.manager_post_data, follow=True)

        self.assertRedirects(response, self.url)
        self.assertTrue(Manager.objects.filter(user=self.user).exists())

    def test_post_invalid_manager_form_data(self):
        self.rm.set_roles(['Manager'])
        self.manager_post_data['manager-team'] = ''
        response = self.client.post(self.url, data=self.manager_post_data, follow=True)
        self.assertFormError(response, 'manager_form', 'team', 'This field is required.')

    def test_post_valid_hockeyplayer_form_data(self):
        self.rm.set_roles(['Player'])
        response = self.client.post(self.url, data=self.hockeyplayer_post_data, follow=True)
        self.assertRedirects(response, self.url)
        self.assertTrue(HockeyPlayer.objects.filter(user=self.user).exists())

    def test_post_invalid_hockeyplayer_form_data(self):
        self.rm.set_roles(['Player'])
        self.hockeyplayer_post_data['hockeyplayer-position'] = ''
        response = self.client.post(self.url, data=self.hockeyplayer_post_data, follow=True)
        self.assertFormError(response, 'player_form', 'position', 'This field is required.')

    def test_post_valid_coach_and_manager_forms(self):
        self.rm.set_roles(['Coach', 'Manager'])
        post_data = self.manager_post_data.copy()
        post_data.update(self.coach_post_data)
        response = self.client.post(self.url, data=post_data, follow=True)
        self.assertRedirects(response, self.url)
        self.assertTrue(Manager.objects.filter(user=self.user).exists())
        self.assertTrue(Coach.objects.filter(user=self.user).exists())

    def test_post_invalid_coach_manager_forms(self):
        self.rm.set_roles(['Coach', 'Manager'])
        post_data = self.manager_post_data.copy()
        post_data.update(self.coach_post_data)
        del post_data['coach-position']
        del post_data['manager-team']
        response = self.client.post(self.url, data=post_data, follow=True)
        self.assertFormError(response, 'coach_form', 'position', 'This field is required.')
        self.assertFormError(response, 'manager_form', 'team', 'This field is required.')

    def test_post_valid_coach_manager_referee_forms(self):
        self.rm.set_roles(['Coach', 'Manager', 'Referee'])
        post_data = self.manager_post_data.copy()
        post_data.update(self.coach_post_data)
        post_data.update(self.referee_post_data)

        response = self.client.post(self.url, data=post_data, follow=True)

        self.assertRedirects(response, self.url)
        self.assertTrue(Manager.objects.filter(user=self.user).exists())
        self.assertTrue(Coach.objects.filter(user=self.user).exists())
        self.assertTrue(Referee.objects.filter(user=self.user).exists())

    def test_post_invalid_coach_manager_referee_forms(self):
        self.rm.set_roles(['Coach', 'Manager', 'Referee'])
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
        self.rm.set_roles(['Coach', 'Manager', 'Referee', 'Player'])
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
        self.rm.set_roles(['Coach', 'Manager', 'Referee', 'Player'])
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
        self.rm.set_roles(['Coach', 'Manager'])
        post_data = self.manager_post_data.copy()
        post_data.update(self.coach_post_data)
        # Coach form is invalid
        del post_data['coach-position']
        response = self.client.post(self.url, data=post_data, follow=True)
        self.assertFormError(response, 'coach_form', 'position', 'This field is required.')
        self.assertFalse(Manager.objects.filter(user=self.user).exists())
        self.assertFalse(Coach.objects.filter(user=self.user).exists())

    def test_next_role_mask_fetched(self):
        response = self.client.post(self.url, data=self.coach_post_data, follow=True)
        self.assertTrue(response.context['roles_masks_exist'])
        self.assertRedirects(response, self.url)
        self.assertTrue(RolesMask.objects.get(user=self.user, sport=self.rm.sport).are_role_objects_created)
