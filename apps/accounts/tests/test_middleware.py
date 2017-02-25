from unittest.mock import Mock

from django.urls import reverse

from accounts.tests import UserFactory
from coaches.tests import CoachFactory
from escoresheet.utils.testing_utils import BaseTestCase
from leagues.tests import LeagueFactory
from players.tests import HockeyPlayerFactory
from referees.tests import RefereeFactory
from sports.tests import SportFactory, SportRegistrationFactory
from ..middleware import AccountAndSportRegistrationCompleteMiddleware


class AccountAndSportRegistrationCompleteMiddlewareTests(BaseTestCase):
    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.baseball = SportFactory(name='Baseball')
        self.password = 'myweakpassword'
        self.user_with_profile = UserFactory(password=self.password)
        self.user_without_profile = UserFactory(password=self.password, userprofile=None)

    def test_anonymous_user(self):
        """
        Requests by anonymous users should be allowed through. (i.e. contact, about, anonymous home page, etc.)
        """
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home/anonymous_home.html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response, 'userprofiles/userprofile_create.html')
        self.assertTemplateNotUsed(response, 'sports/sport_registration_create.html')

    # Testing whitelisted urls
    def test_no_redirect_loop_create_profile_url(self):
        """
        Make sure accessing a whitelisted url does not lead to a redirect loop
        """
        self.client.login(email=self.user_without_profile.email, password=self.password)
        response = self.client.get(reverse('account_complete_registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userprofiles/userprofile_create.html')

    def test_no_redirect_loop_create_sport_registration_url(self):
        """
        Make sure accessing a whitelisted url does not lead to a redirect loop
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        response = self.client.get(reverse('sportregistrations:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sports/sport_registration_create.html')

    def test_no_redirect_loop_create_players_url(self):
        """
        Make sure accessing a whitelisted url does not lead to a redirect loop
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        sr = SportRegistrationFactory(user=self.user_with_profile, sport=self.ice_hockey, is_complete=False)
        SportRegistrationFactory(user=self.user_with_profile, sport=self.baseball, is_complete=False)
        response = self.client.get(reverse('sportregistrations:players:create', kwargs={'pk': sr.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'players/players_create.html')

    def test_no_redirect_on_logout(self):
        """
        Make sure accessing a whitelisted url does not lead to a redirect loop
        """
        self.client.login(email=self.user_without_profile.email, password=self.password)
        response = self.client.get(reverse('account_logout'))
        self.assertTemplateUsed(response, 'account/logout.html')
        self.assertTemplateNotUsed(response, 'userprofiles/userprofile_create.html')
        self.assertTemplateNotUsed(response, 'sports/sport_registration_create.html')
        self.assertEqual(response.status_code, 200)

    def test_no_sport_registrations(self):
        """
        A user without any sport registrations should be prompted to create one.
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('sportregistrations:create'))

    def test_no_userprofile(self):
        """
        A user without a userprofile should be prompted to create one.
        """
        self.client.login(email=self.user_without_profile.email, password=self.password)
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('account_complete_registration'))

    def test_no_roles_completed(self):
        """
        A user with incomplete sport registrations and no roles completed (player, coach, referee, manager objects DNE)
        should be redirected to the appropriate page to create the appropriate related role objects.
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        sr = SportRegistrationFactory(user=self.user_with_profile, sport=self.ice_hockey, is_complete=False)
        sr.set_roles(['Player', 'Coach', 'Referee', 'Manager'])
        SportRegistrationFactory(user=self.user_with_profile, sport=self.baseball, is_complete=False)
        response = self.client.get(reverse('home'))
        url = reverse('sportregistrations:players:create', kwargs={'pk': sr.id})
        self.assertRedirects(response, url)

    def test_player_role_completed(self):
        """
        Should redirect to page to create coaches
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        sr = SportRegistrationFactory(user=self.user_with_profile, sport=self.ice_hockey, is_complete=False)
        sr.set_roles(['Player', 'Coach', 'Referee', 'Manager'])
        HockeyPlayerFactory(user=self.user_with_profile, sport=self.ice_hockey)
        response = self.client.get(reverse('home'))
        url = reverse('sportregistrations:coaches:create', kwargs={'pk': sr.id})
        self.assertRedirects(response, url)

    def test_coach_role_completed(self):
        """
        Should redirect to page to create referees
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        sr = SportRegistrationFactory(user=self.user_with_profile, sport=self.ice_hockey, is_complete=False)
        sr.set_roles(['Player', 'Coach', 'Referee', 'Manager'])
        HockeyPlayerFactory(user=self.user_with_profile, sport=self.ice_hockey)
        CoachFactory(user=self.user_with_profile, team__division__league__sport=self.ice_hockey)
        response = self.client.get(reverse('home'))
        url = reverse('sportregistrations:referees:create', kwargs={'pk': sr.id})
        self.assertRedirects(response, url)

    def test_referee_role_completed(self):
        """
        Should redirect to page to create managers
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        league = LeagueFactory(sport=self.ice_hockey, full_name='Long Island Amateur Hockey League')
        sr = SportRegistrationFactory(user=self.user_with_profile, sport=self.ice_hockey, is_complete=False)
        sr.set_roles(['Player', 'Coach', 'Referee', 'Manager'])
        HockeyPlayerFactory(user=self.user_with_profile, sport=self.ice_hockey)
        CoachFactory(user=self.user_with_profile, team__division__league=league)
        RefereeFactory(user=self.user_with_profile, league=league)
        response = self.client.get(reverse('home'))
        url = reverse('sportregistrations:managers:create', kwargs={'pk': sr.id})
        self.assertRedirects(response, url)

    # Testing manager role complete is really just testing sr.is_complete = True.

    def test_single_role(self):
        """
        Should redirect to page to create coaches
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        sr = SportRegistrationFactory(user=self.user_with_profile, sport=self.ice_hockey, is_complete=False)
        sr.set_roles(['Coach'])
        response = self.client.get(reverse('home'))
        url = reverse('sportregistrations:coaches:create', kwargs={'pk': sr.id})
        self.assertRedirects(response, url)

    def test_account_completed(self):
        """
        A user with a valid profile, and at least one complete sport registration should be able to access any page url
        without the middleware kicking in
        """
        self.client.login(email=self.user_with_profile.email, password=self.password)
        SportRegistrationFactory(user=self.user_with_profile, sport=self.ice_hockey, is_complete=True)
        SportRegistrationFactory(user=self.user_with_profile, sport=self.baseball, is_complete=True)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/authenticated_home.html')


class MiddlewareAddsRolesToSessionTests(BaseTestCase):
    """
    This tests to make sure the middleware is adding the user roles to the session correctly
    """

    @classmethod
    def setUpClass(cls):
        super(MiddlewareAddsRolesToSessionTests, cls).setUpClass()
        cls.user = UserFactory(email='user@example.com', password='myweakpassword')
        cls.ice_hockey = SportFactory(name='Ice Hockey')
        cls.baseball = SportFactory(name='Baseball')

    def setUp(self):
        self.middleware = AccountAndSportRegistrationCompleteMiddleware()
        self.hockey_sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey, is_complete=True)
        self.baseball_sr = SportRegistrationFactory(user=self.user, sport=self.baseball, is_complete=True)
        self.request = Mock()
        self.request.configure_mock(**{'user': self.user, 'user.is_authenticated.return_value': True})
        self.request.path = '/'
        self.request.session = {}

    def test_single_sport_registration(self):
        self.hockey_sr.set_roles(['Player', 'Coach'])
        self.middleware.process_request(self.request)
        self.assertListEqual(['Player', 'Coach'], self.request.session.get('user_roles'))

    def test_multiple_sport_registrations(self):
        """
        This tests that all roles from all sport registrations are added to the session
        """
        self.hockey_sr.set_roles(['Referee'])
        self.baseball_sr.set_roles(['Manager'])
        self.middleware.process_request(self.request)
        self.assertListEqual(['Referee', 'Manager'], self.request.session.get('user_roles'))

    def test_same_role_not_duplicated(self):
        self.hockey_sr.set_roles(['Player', 'Coach', 'Referee'])
        self.baseball_sr.set_roles(['Coach', 'Manager'])
        self.middleware.process_request(self.request)

        self.assertEqual(self.request.session.get('user_roles').count('Coach'), 1)
