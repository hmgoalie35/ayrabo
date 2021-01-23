import os
from datetime import date

from allauth.account.models import EmailAddress
from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ayrabo.utils.testing import BaseTestCase
from coaches.tests import CoachFactory
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from referees.tests import RefereeFactory
from scorekeepers.tests import ScorekeeperFactory
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
from userprofiles.models import UserProfile
from userprofiles.tests import UserProfileFactory
from users.models import User
from users.tests import UserFactory


class UserDetailViewTests(BaseTestCase):
    url = 'users:detail'

    def setUp(self):
        self.user = UserFactory(first_name='Michael', last_name='Scarn', userprofile=None)
        self.birthday = date(year=1994, month=3, day=22)
        self.user_profile = UserProfileFactory(user=self.user, height='5\' 7"', weight=155, gender=UserProfile.MALE,
                                               birthday=self.birthday, timezone='US/Eastern')
        self.user2 = UserFactory(first_name='Mose', last_name='Schrute', userprofile=None)
        self.birthday2 = date(year=1996, month=2, day=23)
        self.user_profile2 = UserProfileFactory(user=self.user2, height='6\' 5"', weight=225, gender=UserProfile.MALE,
                                                birthday=self.birthday2, timezone='UTC')
        self.formatted_url = self.format_url(pk=self.user2.pk)
        self.login(user=self.user)

    # General
    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.formatted_url)

    # GET
    def test_get(self):
        ice_hockey = SportFactory(name='Ice Hockey')
        liahl = LeagueFactory(sport=ice_hockey, name='Long Island Amateur Hockey League')
        mm_aa = DivisionFactory(league=liahl, name='Midget Minor AA')
        icecats = TeamFactory(name='Green Machine IceCats', division=mm_aa)
        SportRegistrationFactory(user=self.user2, sport=ice_hockey, role=SportRegistration.COACH)
        SportRegistrationFactory(user=self.user2, sport=ice_hockey, role=SportRegistration.MANAGER)
        CoachFactory(team=icecats, user=self.user2)
        ManagerFactory(team=icecats, user=self.user2)

        baseball = SportFactory(name='Baseball')
        mlb = LeagueFactory(name='Major League Baseball', sport=baseball)
        SportRegistrationFactory(user=self.user2, sport=baseball, role=SportRegistration.REFEREE)
        SportRegistrationFactory(user=self.user2, sport=baseball, role=SportRegistration.SCOREKEEPER)
        RefereeFactory(user=self.user2, league=mlb)
        ScorekeeperFactory(user=self.user2, sport=baseball)

        # User viewing user2
        response = self.client.get(self.formatted_url)
        context = response.context
        user_info = context.get('user_information')
        sport_registration_data_by_sport = context.get('sport_registration_data_by_sport')

        # Don't need to go crazy testing the get user detail view context util
        self.assertEqual(context.get('info_tab_link'), 'information')
        self.assertEqual(context.get('sports_tab_link'), 'sports')
        self.assertTrue(context.get('dynamic'))

        self.assertEqual(context.get('user_obj'), self.user2)
        self.assertEqual(context.get('user'), self.user)
        self.assertEqual(context.get('active_tab'), 'information')
        self.assertDictEqual(user_info, {
            'Gender': 'Male',
            # We really just care this key exists in the dict, the unit tests for the age property ensure it will return
            # the correct value.
            'Age': self.user_profile2.age,
            'Birthday': self.birthday2,
            'Height': '6\' 5"',
            'Weight': 225,
            'Timezone': 'UTC'
        })
        self.assertListEqual(list(sport_registration_data_by_sport.keys()), [baseball, ice_hockey])

    def test_get_no_userprofile(self):
        user = UserFactory(first_name='Jon', last_name='Doe', userprofile=None)
        response = self.client.get(self.format_url(pk=user.pk))
        context = response.context
        self.assert_200(response)
        self.assertDictEqual(context.get('user_information'), {})


class UserUpdateViewTests(BaseTestCase):
    url = 'users:update'

    def setUp(self):
        self.first_name = 'Stanley'
        self.last_name = 'Hudson'
        self.birthday = date(year=1997, month=3, day=10)
        self.gender = UserProfile.MALE
        self.height = '6\' 7"'
        self.weight = 255
        self.timezone = 'US/Eastern'
        self.user = UserFactory(first_name=self.first_name, last_name=self.last_name, userprofile=None)
        self.user_profile = UserProfileFactory(user=self.user, height=self.height, weight=self.weight,
                                               gender=self.gender, birthday=self.birthday, timezone=self.timezone)

        self.data = {
            'user-first_name': self.first_name,
            'user-last_name': self.last_name,
            'user_profile-gender': self.gender,
            'user_profile-birthday': self.birthday,
            'user_profile-height': self.height,
            'user_profile-weight': self.weight,
            'user_profile-timezone': self.timezone,
        }
        self.login(user=self.user)

    # General
    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.format_url())

    # GET
    def test_get(self):
        response = self.client.get(self.format_url())
        context = response.context

        self.assert_200(response)
        self.assertTemplateUsed('users/user_update.html')

        self.assertIsNotNone(context.get('user_form'))
        self.assertIsNotNone(context.get('user_profile_form'))
        self.assertEqual(context.get('active_tab'), 'information')

        self.assertFalse(context.get('dynamic'))
        self.assertEqual(context.get('user_obj'), self.user)

    # POST
    def test_valid_post(self):
        self.data.update({
            'user-first_name': 'Jim',
            'user-last_name': 'Halpert',
            'user_profile-weight': 125,
        })
        response = self.client.post(self.format_url(), data=self.data, follow=True)
        self.user.refresh_from_db()
        self.user_profile.refresh_from_db()

        self.assertHasMessage(response, 'Your account information has been updated.')
        self.assertRedirects(response, reverse('users:detail', kwargs={'pk': self.user.pk}))
        self.assertEqual(self.user.first_name, 'Jim')
        self.assertEqual(self.user.last_name, 'Halpert')
        self.assertEqual(self.user.userprofile.weight, 125)

    def test_valid_post_nothing_changed(self):
        response = self.client.post(self.format_url(), data=self.data, follow=True)
        self.assertNoMessage(response, 'Your account information has been updated.')
        self.assertRedirects(response, reverse('users:detail', kwargs={'pk': self.user.pk}))

    def test_invalid_post(self):
        self.data.update({
            'user-first_name': 'a' * 35,
            'user_profile-height': "5' 5'"
        })
        response = self.client.post(self.format_url(), data=self.data)
        self.assertTemplateUsed('users/user_update.html')
        self.assertFormError(response, 'user_form', 'first_name',
                             'Ensure this value has at most 30 characters (it has 35).')
        self.assertFormError(response, 'user_profile_form', 'height',
                             'Invalid format, please enter your height according to the format below.')


class UserAdminBulkUploadViewTests(BaseTestCase):
    url = 'admin:users_user_bulk_upload'

    def setUp(self):
        self.url = self.format_url()
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password, is_staff=True, is_superuser=True)
        self.login(email=self.email, password=self.password)

    def test_post_valid_csv(self):
        with open(os.path.join(settings.STATIC_DIR, 'csv_examples', 'bulk_upload_users_example.csv')) as f:
            response = self.client.post(self.url, {'file': f}, follow=True)
            u = User.objects.get(email='test@ayrabo.com')
            email_address = EmailAddress.objects.get(user=u)

            self.assertHasMessage(response, 'Successfully created 1 user')
            self.assertEqual(u.username, 'test@ayrabo.com')
            self.assertEqual(u.first_name, 'Test')
            self.assertEqual(u.last_name, 'User')
            self.assertFalse(u.has_usable_password())
            self.assertEqual(email_address.email, 'test@ayrabo.com')
            self.assertTrue(email_address.primary)
            self.assertFalse(email_address.verified)

            welcome_email = mail.outbox[0]
            confirmation_email = mail.outbox[1]
            self.assertEqual('Welcome to ayrabo!', welcome_email.subject)
            self.assertEqual('[ayrabo] Please Confirm Your E-mail Address', confirmation_email.subject)

    def test_post_invalid_csv(self):
        header = ['email', 'first_name', 'last_name']
        row = ['', 'Test', 'User']
        content = f'{",".join(header)}\n{",".join(row)}'.encode()
        f = SimpleUploadedFile('test.csv', content)
        response = self.client.post(self.url, {'file': f}, follow=True)
        self.assertListEqual(list(User.objects.values_list('email', flat=True)), [self.email])
        self.assertFormsetError(
            response,
            'formset',
            0,
            'email',
            ['This field is required.']
        )
