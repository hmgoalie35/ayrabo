from django.test import TestCase
from accounts.tests.factories.UserFactory import UserFactory
from .factories.UserProfileFactory import UserProfileFactory
from django.core.urlresolvers import reverse
import factory
from userprofiles.models import UserProfile
from escoresheet.testing_utils import get_messages


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
        response = self.client.post(reverse('create_userprofile'), data=data)
        result_url = '%s?next=%s' % (reverse('account_login'), reverse('create_userprofile'))
        self.assertRedirects(response, result_url)

    def test_post_userprofile_already_created(self):
        self.client.logout()
        user_with_profile = UserFactory.create(password=self.password)
        self.client.login(email=user_with_profile.email, password=self.password)
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        response = self.client.post(reverse('create_userprofile'), data=data, follow=True)
        self.assertRedirects(response, reverse('home'))

    def test_valid_post_data(self):
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        response = self.client.post(reverse('create_userprofile'), data=data, follow=True)
        success_msg = 'Thank you for filling out your profile, you now have access to the entire site'
        self.assertIn(success_msg, get_messages(response))
        self.assertRedirects(response, reverse('home'))

    def test_user_attribute_is_set(self):
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        self.client.post(reverse('create_userprofile'), data=data, follow=True)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    # Invalid POST data
    def test_no_height_weight_gender(self):
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        data.pop('gender')
        data.pop('height')
        data.pop('weight')
        response = self.client.post(reverse('create_userprofile'), data=data, follow=True)
        self.assertFormError(response, 'form', 'gender', 'This field is required.')
        self.assertFormError(response, 'form', 'height', 'This field is required.')
        self.assertFormError(response, 'form', 'weight', 'This field is required.')

    def test_invaild_height_format(self):
        invalid_heights = ['5 7', '5 7\"', '5\' 7']
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        for invalid_height in invalid_heights:
            data['height'] = invalid_height
            response = self.client.post(reverse('create_userprofile'), data=data, follow=True)
            self.assertFormError(response, 'form', 'height', 'Invalid format, please use the following format: 5\' 7"')

    def test_negative_and_zero_weights(self):
        invalid_weights = [-1, -100, 0]
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        for invalid_weight in invalid_weights:
            data['weight'] = invalid_weight
            response = self.client.post(reverse('create_userprofile'), data=data, follow=True)
            self.assertFormError(response, 'form', 'weight', 'Weight must be greater than zero and less than 400')

    def test_decimal_weights(self):
        invalid_weights = [.5, -.5]
        data = factory.build(dict, FACTORY_CLASS=UserProfileFactory)
        for invalid_weight in invalid_weights:
            data['weight'] = invalid_weight
            response = self.client.post(reverse('create_userprofile'), data=data, follow=True)
            self.assertFormError(response, 'form', 'weight', 'Enter a whole number.')
