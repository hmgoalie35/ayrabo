from datetime import date

from ayrabo.utils.testing import BaseTestCase
from coaches.tests import CoachFactory
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from managers.tests import ManagerFactory
from referees.tests import RefereeFactory
from scorekeepers.tests import ScorekeeperFactory
from sports.tests import SportFactory, SportRegistrationFactory
from teams.tests import TeamFactory
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
        ice_hockey = SportFactory(name='Ice Hockey')
        liahl = LeagueFactory(sport=ice_hockey, name='Long Island Amateur Hockey League')
        mm_aa = DivisionFactory(league=liahl, name='Midget Minor AA')
        icecats = TeamFactory(name='Green Machine IceCats', division=mm_aa)
        SportRegistrationFactory(user=self.user2, sport=ice_hockey, role='coach')
        SportRegistrationFactory(user=self.user2, sport=ice_hockey, role='manager')
        CoachFactory(team=icecats, user=self.user2)
        ManagerFactory(team=icecats, user=self.user2)

        baseball = SportFactory(name='Baseball')
        mlb = LeagueFactory(name='Major League Baseball', sport=baseball)
        SportRegistrationFactory(user=self.user2, sport=baseball, role='referee')
        SportRegistrationFactory(user=self.user2, sport=baseball, role='scorekeeper')
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
