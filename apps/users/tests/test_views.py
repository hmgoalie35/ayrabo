from datetime import date

from ayrabo.utils.testing import BaseTestCase
from userprofiles.tests import UserProfileFactory
from users.tests import UserFactory


class UserDetailViewTests(BaseTestCase):
    url = 'users:detail'

    def setUp(self):
        self.user = UserFactory(first_name='Michael', last_name='Scarn', userprofile=None)
        self.birthday = date(year=1994, month=3, day=22)
        self.user_profile = UserProfileFactory(user=self.user, height='5\' 7"', weight=155, gender='male',
                                               birthday=self.birthday, timezone='US/Eastern')
        self.user2 = UserFactory(first_name='Mose', last_name='Schrute', userprofile=None)
        self.birthday2 = date(year=1996, month=2, day=23)
        self.user_profile2 = UserProfileFactory(user=self.user2, height='6\' 5"', weight=225, gender='male',
                                                birthday=self.birthday2, timezone='UTC')
        self.formatted_url = self.format_url(pk=self.user2.pk)
        self.login(user=self.user)

    # General
    def test_login_required(self):
        self.client.logout()
        self.assertLoginRequired(self.formatted_url)

    # GET
    def test_get(self):
        # User viewing user2
        response = self.client.get(self.formatted_url)
        context = response.context
        user_info = context.get('user_information')

        self.assertEqual(context.get('info_tab_key'), 'information')
        self.assertEqual(context.get('sports_tab_key'), 'sports')
        self.assertEqual(context.get('active_tab'), 'information')
        self.assertEqual(user_info.get('Gender'), 'Male')
        self.assertEqual(user_info.get('Birthday'), self.birthday2)
        self.assertEqual(user_info.get('Height'), '6\' 5"')
        self.assertEqual(user_info.get('Weight'), 225)
        self.assertEqual(user_info.get('Timezone'), 'UTC')
