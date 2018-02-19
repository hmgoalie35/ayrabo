from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from users.tests import UserFactory
from api.tests import TokenFactory
from sports.tests import SportRegistrationFactory


class ObtainAuthTokenTests(APITestCase):
    """
    You do not need to be authenticated to hit this endpoint.
    If you already have an api token, a new token will not be generated for you. You will receive your original token.
    """

    def test_token_created(self):
        email = 'user@ayrabo.com'
        password = 'myweakpassword'
        user = UserFactory(email=email, password=password)
        response = self.client.post(reverse('obtain_api_token'), data={'username': email, 'password': password})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], Token.objects.get(user=user).key)


class RevokeAuthTokenTests(APITestCase):
    def setUp(self):
        self.email = 'user@ayrabo.com'
        self.password = 'myweakpassword'
        self.user = UserFactory(email=self.email, password=self.password)
        SportRegistrationFactory(user=self.user)
        self.client.login(username=self.email, password=self.password)

    def test_token_exists(self):
        TokenFactory(user=self.user)
        response = self.client.delete(reverse('revoke_api_token'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Token.objects.count(), 0)

    def test_token_dne(self):
        response = self.client.delete(reverse('revoke_api_token'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class APIHomeTests(APITestCase):
    def test_api_home(self):
        response = self.client.get(reverse('api_home'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'api/api_home.html')
