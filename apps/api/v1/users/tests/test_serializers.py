from accounts.tests import UserFactory
from api.v1.users.serializers import UserSerializer
from ayrabo.utils.testing import BaseAPITestCase


class UserSerializerTests(BaseAPITestCase):
    serializer_class = UserSerializer

    def test_fields(self):
        user = UserFactory(id=1, first_name='Michael', last_name='Scott')
        data = self.serializer_class(instance=user).data
        self.assertDictEqual(data, {
            'id': 1,
            'first_name': 'Michael',
            'last_name': 'Scott'
        })
