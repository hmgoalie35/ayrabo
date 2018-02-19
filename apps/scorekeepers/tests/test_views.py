from django.urls import reverse

from accounts.tests import UserFactory
from coaches.tests import CoachFactory
from ayrabo.utils.testing import BaseTestCase
from managers.tests import ManagerFactory
from scorekeepers.models import Scorekeeper
from scorekeepers.tests import ScorekeeperFactory
from sports.tests import SportRegistrationFactory, SportFactory
from teams.tests import TeamFactory


class ScorekeepersCreateViewTests(BaseTestCase):
    url = 'sportregistrations:scorekeepers:create'

    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.baseball = SportFactory(name='Baseball')
        self.hockey_team = TeamFactory(division__league__sport=self.ice_hockey)
        self.baseball_team = TeamFactory(division__league__sport=self.baseball)

        self.email = 'user@example.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)
        self.sr = SportRegistrationFactory(user=self.user, sport=self.ice_hockey)
        self.sr.set_roles(['Manager'])
        ManagerFactory(user=self.user, team=self.hockey_team)

    # General
    def test_login_required(self):
        url = self.format_url(pk=self.sr.id)
        response = self.client.post(url)
        self.assertRedirects(response, self.get_login_required_url(url))

    def test_has_permission(self):
        user = UserFactory()
        sr = SportRegistrationFactory(user=user, sport=self.ice_hockey)
        sr.set_roles(['Manager'])
        ManagerFactory(user=user, team=self.hockey_team)
        self.login(user=user)
        response = self.client.post(self.format_url(pk=self.sr.id))
        self.assert_404(response)

    # POST
    def test_sport_registration_dne(self):
        self.login(user=self.user)
        response = self.client.post(self.format_url(pk=1000))
        self.assert_404(response)

    def test_user_already_scorekeeper_for_all_sports(self):
        sr = SportRegistrationFactory(user=self.user, sport=self.baseball)
        sr.set_roles(['Coach'])
        CoachFactory(user=self.user, team=self.baseball_team, is_active=False)
        ScorekeeperFactory(user=self.user, sport=self.ice_hockey)
        ScorekeeperFactory(user=self.user, sport=self.baseball)

        self.login(user=self.user)
        response = self.client.post(self.format_url(pk=self.sr.id), follow=True)
        self.assertRedirects(response, reverse('sportregistrations:detail', kwargs={'pk': self.sr.id}))
        self.assertHasMessage(response, 'You have already registered for all available sports. Please contact us to '
                                        'reactivate your scorekeeper registration.')

    def test_user_already_inactive_scorekeeper_for_sport(self):
        ScorekeeperFactory(user=self.user, sport=self.ice_hockey, is_active=False)
        self.login(user=self.user)
        response = self.client.post(self.format_url(pk=self.sr.id), follow=True)
        self.assertRedirects(response, reverse('sportregistrations:detail', kwargs={'pk': self.sr.id}))
        self.assertHasMessage(response, 'Trying to reactivate your scorekeeper registration? Contact us.')

    def test_user_already_active_scorekeeper_for_sport(self):
        ScorekeeperFactory(user=self.user, sport=self.ice_hockey, is_active=True)
        self.login(user=self.user)
        response = self.client.post(self.format_url(pk=self.sr.id), follow=True)
        self.assertRedirects(response, reverse('sportregistrations:detail', kwargs={'pk': self.sr.id}))

    def test_valid_post(self):
        self.login(user=self.user)
        response = self.client.post(self.format_url(pk=self.sr.id), follow=True)
        self.assertRedirects(response, reverse('sportregistrations:detail', kwargs={'pk': self.sr.id}))
        self.assertHasMessage(response, 'You have been registered as a scorekeeper for Ice Hockey.')
        self.assertEqual(Scorekeeper.objects.count(), 1)
        self.sr.refresh_from_db()
        self.assertTrue(self.sr.has_role('Scorekeeper'))
