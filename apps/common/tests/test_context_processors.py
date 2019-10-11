from ayrabo.utils.testing import BaseTestCase
from sports.models import SportRegistration
from sports.tests import SportFactory, SportRegistrationFactory
from users.tests import UserFactory


class ContextProcessorTests(BaseTestCase):
    url = 'home'

    def test_support_contact(self):
        response = self.client.get(self.format_url())
        context = response.context
        self.assertEqual(context.get('support_contact'), {
            'email': 'support@ayrabo.com',
            'name': 'Harris Pittinsky'
        })

    def test_sports_for_user_anonymous(self):
        response = self.client.get(self.format_url())
        context = response.context
        self.assertEqual(context.get('sports_for_user'), [])

    def test_sports_for_user_authenticated(self):
        user = UserFactory()
        ice_hockey = SportFactory(name='Ice Hockey')
        baseball = SportFactory(name='Baseball')
        SportRegistrationFactory(user=user, role=SportRegistration.COACH, sport=ice_hockey)
        SportRegistrationFactory(user=user, role=SportRegistration.PLAYER, sport=ice_hockey)
        SportRegistrationFactory(user=user, role=SportRegistration.MANAGER, sport=ice_hockey)
        SportRegistrationFactory(user=user, role=SportRegistration.PLAYER, sport=baseball)
        SportRegistrationFactory(user=user, role=SportRegistration.REFEREE, sport=baseball)
        self.login(user=user)
        response = self.client.get(self.format_url())
        context = response.context
        self.assertEqual(context.get('sports_for_user'), [baseball, ice_hockey])
