import factory
from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.tests.factories.UserFactory import UserFactory
from coaches.models import Coach
from coaches.tests.factories.CoachFactory import CoachFactory
from divisions.tests.factories.DivisionFactory import DivisionFactory
from escoresheet.testing_utils import get_messages
from managers.models import Manager
from managers.tests.factories.ManagerFactory import ManagerFactory
from teams.tests.factories.TeamFactory import TeamFactory
from userprofiles.models import UserProfile
from .factories.UserProfileFactory import UserProfileFactory


class CreateUserProfileViewTests(TestCase):
    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.post_data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        del self.post_data['roles_mask']
        self.post_data['roles'] = ['Player']
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

    def test_get_userprofile_already_created(self):
        self.client.logout()
        user_with_profile = UserFactory.create(password=self.password)
        self.client.login(email=user_with_profile.email, password=self.password)
        response = self.client.get(reverse('profile:create'))
        self.assertRedirects(response, reverse('home'))

    # POST
    def test_post_anonymous_user(self):
        self.client.logout()
        response = self.client.post(reverse('profile:create'), data=self.post_data)
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('profile:create'))
        self.assertRedirects(response, result_url)

    def test_post_userprofile_already_created(self):
        self.client.logout()
        user_with_profile = UserFactory.create(password=self.password)
        self.client.login(email=user_with_profile.email, password=self.password)
        response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('home'))

    def test_valid_post_data(self):
        response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('profile:finish'))

    def test_user_attribute_is_set(self):
        self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_roles_are_set(self):
        self.post_data['roles'] = ['Player', 'Manager']
        self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertListEqual(self.user.userprofile.roles, self.post_data['roles'])
        self.assertEqual(self.user.userprofile.roles_mask, 9)

    # Invalid POST data
    def test_no_height_weight_gender(self):
        self.post_data.pop('gender')
        self.post_data.pop('height')
        self.post_data.pop('weight')
        response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertFormError(response, 'form', 'gender', 'This field is required.')
        self.assertFormError(response, 'form', 'height', 'This field is required.')
        self.assertFormError(response, 'form', 'weight', 'This field is required.')

    def test_invaild_height_format(self):
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
            self.assertFormError(response, 'form', 'weight', 'Weight must be greater than zero and less than 400')

    def test_decimal_weights(self):
        invalid_weights = [.5, -.5]
        for invalid_weight in invalid_weights:
            self.post_data['weight'] = invalid_weight
            response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
            self.assertFormError(response, 'form', 'weight', 'Enter a whole number.')

    def test_no_roles(self):
        self.post_data['roles'] = []
        response = self.client.post(reverse('profile:create'), data=self.post_data, follow=True)
        self.assertFormError(response, 'form', 'roles', 'This field is required.')


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


class FinishUserProfileViewTests(TestCase):
    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'

        self.coach_post_data = factory.build(dict, FACTORY_CLASS=CoachFactory)
        self.coach_post_data['coach-position'] = self.coach_post_data.pop('position')

        self.manager_post_data = factory.build(dict, FACTORY_CLASS=ManagerFactory)
        self.division = DivisionFactory(name='Midget Minor AA')
        self.team = TeamFactory(name='Green Machine IceCats', division=self.division)

        self.coach_post_data['coach-team'] = str(self.team.id)
        self.manager_post_data['manager-team'] = str(self.team.id)
        del self.coach_post_data['user']
        del self.manager_post_data['user']

        self.user = UserFactory.create(email=self.email, password=self.password)
        self.user.userprofile.is_complete = False
        self.user.userprofile.set_roles(['Coach'])
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse('profile:finish'))
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('profile:finish'))
        self.assertRedirects(response, result_url)

    def test_renders_correct_template(self):
        response = self.client.get(reverse('profile:finish'))
        self.assertTemplateUsed(response, 'userprofiles/finish_profile.html')

    def test_200_status_code(self):
        response = self.client.get(reverse('profile:finish'))
        self.assertEqual(response.status_code, 200)

    def test_coach_form_in_context(self):
        """
        Only coach role
        """
        response = self.client.get(reverse('profile:finish'))
        self.assertIn('coach_form', response.context)

    def test_manager_form_in_context(self):
        self.user.userprofile.set_roles(['Manager'])
        response = self.client.get(reverse('profile:finish'))
        self.assertIn('manager_form', response.context)

    def test_all_forms_in_context(self):
        """
        All roles
        """
        self.user.userprofile.set_roles([role for role in UserProfile.ROLES])
        response = self.client.get(reverse('profile:finish'))
        self.assertIn('coach_form', response.context)
        self.assertIn('player_form', response.context)
        self.assertIn('manager_form', response.context)
        self.assertIn('referee_form', response.context)

    def test_coach_player_forms_in_context(self):
        """
        Coach and player roles
        """
        self.user.userprofile.set_roles(['Coach', 'Player'])
        response = self.client.get(reverse('profile:finish'))
        self.assertIn('coach_form', response.context)
        self.assertIn('player_form', response.context)

    def test_get_already_complete_profile(self):
        self.user.userprofile.is_complete = True
        self.user.userprofile.save()
        response = self.client.get(reverse('profile:finish'))
        self.assertRedirects(response, reverse('home'))

    # it's overkill to add in tests for all permutations of UserProfile.ROLES, but might need to do it anyway

    # POST
    def test_post_anonymous_user(self):
        self.client.logout()
        response = self.client.post(reverse('profile:finish'), data=self.coach_post_data, follow=True)
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('profile:finish'))
        self.assertRedirects(response, result_url)

    def test_post_already_complete_profile(self):
        self.user.userprofile.is_complete = True
        self.user.userprofile.save()
        response = self.client.post(reverse('profile:finish'), data=self.coach_post_data, follow=True)
        self.assertRedirects(response, reverse('home'))

    def test_post_valid_coach_form_data(self):
        response = self.client.post(reverse('profile:finish'), data=self.coach_post_data, follow=True)
        self.assertIn('You have successfully completed your profile, you can now access the site',
                      get_messages(response))
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(Coach.objects.filter(user=self.user).exists())

    def test_post_invalid_coach_form_data(self):
        del self.coach_post_data['coach-position']
        response = self.client.post(reverse('profile:finish'), data=self.coach_post_data, follow=True)
        self.assertFormError(response, 'coach_form', 'position', 'This field is required.')

    def test_post_valid_manager_form_data(self):
        self.user.userprofile.set_roles(['Manager'])
        response = self.client.post(reverse('profile:finish'), data=self.manager_post_data, follow=True)
        self.assertIn('You have successfully completed your profile, you can now access the site',
                      get_messages(response))
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(Manager.objects.filter(user=self.user).exists())

    def test_post_invalid_manager_form_data(self):
        self.user.userprofile.set_roles(['Manager'])
        self.manager_post_data['manager-team'] = ''
        response = self.client.post(reverse('profile:finish'), data=self.manager_post_data, follow=True)
        self.assertFormError(response, 'manager_form', 'team', 'This field is required.')

    def test_post_valid_coach_and_manager_forms(self):
        self.user.userprofile.set_roles(['Coach', 'Manager'])
        post_data = self.manager_post_data.copy()
        post_data.update(self.coach_post_data)
        response = self.client.post(reverse('profile:finish'), data=post_data, follow=True)
        self.assertIn('You have successfully completed your profile, you can now access the site',
                      get_messages(response))
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(Manager.objects.filter(user=self.user).exists())
        self.assertTrue(Coach.objects.filter(user=self.user).exists())

    def test_post_invalid_coach_manager_forms(self):
        self.user.userprofile.set_roles(['Coach', 'Manager'])
        post_data = self.manager_post_data.copy()
        post_data.update(self.coach_post_data)
        del post_data['coach-position']
        del post_data['manager-team']
        response = self.client.post(reverse('profile:finish'), data=post_data, follow=True)
        self.assertFormError(response, 'coach_form', 'position', 'This field is required.')
        self.assertFormError(response, 'manager_form', 'team', 'This field is required.')
