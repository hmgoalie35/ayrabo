from rest_framework.authtoken.models import Token

from api.tests import TokenFactory
from ayrabo.utils.testing import BaseAPITestCase
from users.tests import UserFactory


class ObtainAuthTokenTests(BaseAPITestCase):
    url = 'obtain_api_token'

    def test_token_created(self):
        email = 'user@ayrabo.com'
        password = 'myweakpassword'
        user = UserFactory(email=email, password=password)
        response = self.client.post(self.format_url(), data={'username': email, 'password': password})

        self.assert_200(response)
        self.assertEqual(response.data['token'], Token.objects.get(user=user).key)


class RevokeAuthTokenTests(BaseAPITestCase):
    url = 'revoke_api_token'

    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)
        self.client.login(username=self.email, password=self.password)

    def test_login_required(self):
        self.client.logout()
        response = self.client.delete(self.format_url())
        self.assertAPIError(response, 'unauthenticated')

    def test_token_exists(self):
        TokenFactory(user=self.user)
        response = self.client.delete(self.format_url())
        self.assert_204(response)
        self.assertEqual(Token.objects.count(), 0)

    def test_token_dne(self):
        response = self.client.delete(self.format_url())
        self.assertAPIError(response, 'not_found')
