import os
from datetime import date

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from common.tests import WaffleSwitchFactory
from sports.tests import SportFactory, SportRegistrationFactory
from userprofiles.models import UserProfile
from userprofiles.tests import UserProfileFactory
from users.tests import UserFactory


class UserProfileCreateViewTests(BaseTestCase):
    url = 'account_complete_registration'

    def setUp(self):
        self.sport_reg_switch = WaffleSwitchFactory(name='sport_registrations', active=False)
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.baseball = SportFactory(name='Baseball')
        self.post_data = {
            'user_profile-gender': UserProfile.MALE,
            'user_profile-birthday': date(year=2012, month=2, day=2),
            'user_profile-height': '5\' 4"',
            'user_profile-weight': 100,
            'user_profile-timezone': 'US/Eastern'
        }
        self.user = UserFactory.create(email=self.email, password=self.password, userprofile=None)
        self.login(email=self.email, password=self.password)

    # General
    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.format_url())

    def test_sport_registrations_complete_user_has_userprofile(self):
        UserProfileFactory(user=self.user)
        SportRegistrationFactory(user=self.user)
        response = self.client.get(self.format_url(), follow=True)
        self.assertRedirects(response, reverse('home'))

    def test_userprofile_already_created(self):
        self.client.logout()
        user_with_profile = UserFactory.create(password=self.password)
        self.login(email=user_with_profile.email, password=self.password)
        response = self.client.get(self.format_url())
        self.assertRedirects(response, reverse('home'))

    # GET
    def test_get(self):
        response = self.client.get(self.format_url())
        self.assertTemplateUsed(response, 'userprofiles/userprofile_create.html')
        self.assert_200(response)

    # POST
    def test_post_valid_data(self):
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('home'))
        # Make sure `user` is set to request.user on the userprofile instance
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_post_sport_reg_switch_active(self):
        self.sport_reg_switch.active = True
        self.sport_reg_switch.save()
        response = self.client.post(self.format_url(), data=self.post_data, follow=True)
        self.assertRedirects(response, reverse('sports:register'))

    def test_post_invalid_data(self):
        self.post_data.pop('user_profile-gender')
        self.post_data.pop('user_profile-height')
        self.post_data.pop('user_profile-weight')
        self.post_data.pop('user_profile-birthday')

        response = self.client.post(self.format_url(), data=self.post_data)

        self.assertFormError(response, 'form', 'gender', 'This field is required.')
        self.assertFormError(response, 'form', 'height', 'This field is required.')
        self.assertFormError(response, 'form', 'weight', 'This field is required.')
        self.assertFormError(response, 'form', 'birthday', 'This field is required.')

    def test_post_invalid_height_formats(self):
        invalid_heights = ['5 7', '5 7\"', '5\' 7']
        for invalid_height in invalid_heights:
            self.post_data['user_profile-height'] = invalid_height
            response = self.client.post(self.format_url(), data=self.post_data)
            self.assertFormError(response, 'form', 'height',
                                 'Invalid format, please enter your height according to the format below.')

    def test_post_invalid_weights(self):
        invalid_weights = [-1, -100, 0]
        for invalid_weight in invalid_weights:
            self.post_data['user_profile-weight'] = invalid_weight
            response = self.client.post(self.format_url(), data=self.post_data)
            self.assertFormError(response, 'form', 'weight', 'Ensure this value is greater than or equal to 1.')

    def test_post_invalid_decimal_weights(self):
        invalid_weights = [.5, -.5]
        for invalid_weight in invalid_weights:
            self.post_data['user_profile-weight'] = invalid_weight
            response = self.client.post(self.format_url(), data=self.post_data)
            self.assertFormError(response, 'form', 'weight', 'Enter a whole number.')


class UserProfileAdminBulkUploadViewTests(BaseTestCase):
    url = 'admin:userprofiles_userprofile_bulk_upload'

    def setUp(self):
        self.url = self.format_url()
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password, is_staff=True, is_superuser=True)

    def test_post_valid_csv(self):
        self.login(user=self.user)
        user = UserFactory(id=3596, userprofile=None)
        with open(os.path.join(settings.STATIC_DIR, 'csv_examples', 'bulk_upload_userprofiles_example.csv')) as f:
            response = self.client.post(self.url, {'file': f}, follow=True)

            up = user.userprofile

            self.assertHasMessage(response, 'Successfully created 1 user profile')
            self.assertEqual(up.gender, 'male')
            self.assertEqual(up.birthday.isoformat(), '2020-03-13')
            self.assertEqual(up.height, '5\' 6"')
            self.assertEqual(up.weight, 150)
            self.assertEqual(up.timezone, 'US/Eastern')

    def test_post_invalid_csv(self):
        self.login(email=self.email, password=self.password)
        header = ['user', 'gender', 'birthday', 'height', 'weight', 'timezone']
        row = ['', 'M', '2020-03-25', '6\' 0"', '125', 'US/Eastern']
        content = f'{",".join(header)}\n{",".join(row)}'.encode()
        f = SimpleUploadedFile('test.csv', content)
        response = self.client.post(self.url, {'file': f}, follow=True)

        self.assertListEqual(list(UserProfile.objects.values_list('user__email', flat=True)), [self.email])
        self.assertFormsetError(
            response,
            'formset',
            0,
            'user',
            ['This field is required.']
        )
        self.assertFormsetError(
            response,
            'formset',
            0,
            'gender',
            ['Select a valid choice. M is not one of the available choices.']
        )
