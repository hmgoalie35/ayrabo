import factory
from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.tests.factories.UserFactory import UserFactory
from escoresheet.testing_utils import get_messages
from userprofiles.models import UserProfile
from .factories.UserProfileFactory import UserProfileFactory


class CreateUserProfileViewTests(TestCase):
    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory.create(email=self.email, password=self.password, userprofile=None)
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse('create_userprofile'))
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('create_userprofile'))
        self.assertRedirects(response, result_url)

    def test_correct_template(self):
        response = self.client.get(reverse('create_userprofile'))
        self.assertTemplateUsed(response, 'userprofiles/create.html')

    def test_200_status_code(self):
        response = self.client.get(reverse('create_userprofile'))
        self.assertEqual(response.status_code, 200)

    def test_get_userprofile_already_created(self):
        self.client.logout()
        user_with_profile = UserFactory.create(password=self.password)
        self.client.login(email=user_with_profile.email, password=self.password)
        response = self.client.get(reverse('create_userprofile'))
        self.assertRedirects(response, reverse('home'))

    # POST
    def test_post_anonymous_user(self):
        self.client.logout()
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        del data['roles_mask']
        data['roles'] = ['Player']
        response = self.client.post(reverse('create_userprofile'), data=data)
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('create_userprofile'))
        self.assertRedirects(response, result_url)

    def test_post_userprofile_already_created(self):
        self.client.logout()
        user_with_profile = UserFactory.create(password=self.password)
        self.client.login(email=user_with_profile.email, password=self.password)
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        del data['roles_mask']
        data['roles'] = ['Player']
        response = self.client.post(reverse('create_userprofile'), data=data, follow=True)
        self.assertRedirects(response, reverse('home'))

    def test_valid_post_data(self):
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        del data['roles_mask']
        data['roles'] = ['Player']
        response = self.client.post(reverse('create_userprofile'), data=data, follow=True)
        success_msg = 'Thank you for filling out your profile, you now have access to the entire site'
        self.assertIn(success_msg, get_messages(response))
        self.assertRedirects(response, reverse('home'))

    def test_user_attribute_is_set(self):
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        del data['roles_mask']
        data['roles'] = ['Player']
        self.client.post(reverse('create_userprofile'), data=data, follow=True)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_roles_are_set(self):
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        del data['roles_mask']
        data['roles'] = ['Player', 'Manager']
        self.client.post(reverse('create_userprofile'), data=data, follow=True)
        self.assertListEqual(self.user.userprofile.roles, data['roles'])
        self.assertEqual(self.user.userprofile.roles_mask, 9)

    # Invalid POST data
    def test_no_height_weight_gender(self):
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        data.pop('gender')
        data.pop('height')
        data.pop('weight')
        del data['roles_mask']
        data['roles'] = ['Player']
        response = self.client.post(reverse('create_userprofile'), data=data, follow=True)
        self.assertFormError(response, 'form', 'gender', 'This field is required.')
        self.assertFormError(response, 'form', 'height', 'This field is required.')
        self.assertFormError(response, 'form', 'weight', 'This field is required.')

    def test_invaild_height_format(self):
        invalid_heights = ['5 7', '5 7\"', '5\' 7']
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        del data['roles_mask']
        data['roles'] = ['Player']
        for invalid_height in invalid_heights:
            data['height'] = invalid_height
            response = self.client.post(reverse('create_userprofile'), data=data, follow=True)
            self.assertFormError(response, 'form', 'height', 'Invalid format, please use the following format: 5\' 7"')

    def test_negative_and_zero_weights(self):
        invalid_weights = [-1, -100, 0]
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        del data['roles_mask']
        data['roles'] = ['Player']
        for invalid_weight in invalid_weights:
            data['weight'] = invalid_weight
            response = self.client.post(reverse('create_userprofile'), data=data, follow=True)
            self.assertFormError(response, 'form', 'weight', 'Weight must be greater than zero and less than 400')

    def test_decimal_weights(self):
        invalid_weights = [.5, -.5]
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        del data['roles_mask']
        data['roles'] = ['Player']
        for invalid_weight in invalid_weights:
            data['weight'] = invalid_weight
            response = self.client.post(reverse('create_userprofile'), data=data, follow=True)
            self.assertFormError(response, 'form', 'weight', 'Enter a whole number.')

    def test_no_roles(self):
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        del data['roles_mask']
        response = self.client.post(reverse('create_userprofile'), data=data, follow=True)
        self.assertFormError(response, 'form', 'roles', 'This field is required.')


class UpdateUserProfileViewTests(TestCase):
    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory.create(email=self.email, password=self.password)
        self.client.login(email=self.email, password=self.password)

    # GET
    def test_get_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse('update_userprofile'))
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('update_userprofile'))
        self.assertRedirects(response, result_url)

    def test_correct_template(self):
        response = self.client.get(reverse('update_userprofile'))
        self.assertTemplateUsed(response, 'userprofiles/update.html')

    def test_200_status_code(self):
        response = self.client.get(reverse('update_userprofile'))
        self.assertEqual(response.status_code, 200)

    def test_roles_in_context(self):
        response = self.client.get(reverse('update_userprofile'))
        self.assertIn('user_roles', response.context)

    # POST
    # No need to test invalid values for height, weight, etc. That is done above (the forms are almost identical)
    def test_post_anonymous_user(self):
        self.client.logout()
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        data.pop('gender')
        data.pop('birthday')
        del data['roles_mask']
        data['roles'] = ['Player']
        response = self.client.post(reverse('update_userprofile'), data=data, follow=True)
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('update_userprofile'))
        self.assertRedirects(response, result_url)

    def test_post_no_changed_data(self):
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        data.pop('gender')
        data.pop('birthday')
        del data['roles_mask']
        data['roles'] = ['Player']
        response = self.client.post(reverse('update_userprofile'), data=data, follow=True)
        self.assertRedirects(response, reverse('update_userprofile'))

    def test_post_changed_data(self):
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        # calling the factory will generate random values for all fields
        data.pop('gender')
        data.pop('birthday')
        del data['roles_mask']
        data['roles'] = ['Player']
        response = self.client.post(reverse('update_userprofile'), data=data, follow=True)
        success_msg = 'Your profile has been updated'
        self.assertIn(success_msg, get_messages(response))
        self.assertTemplateUsed('userprofiles/update.html')

    def test_userprofile_exists_in_context(self):
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        # calling the factory will generate random values for all fields
        data.pop('gender')
        data.pop('birthday')
        del data['roles_mask']
        data['roles'] = ['Player']
        response = self.client.post(reverse('update_userprofile'), data=data, follow=True)
        self.assertIn('userprofile', response.context)
