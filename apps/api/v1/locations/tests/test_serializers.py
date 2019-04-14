from ayrabo.utils.testing import BaseAPITestCase
from locations.tests import LocationFactory
from ..serializers import LocationSerializer


class LocationSerializerTests(BaseAPITestCase):
    serializer_cls = LocationSerializer

    def setUp(self) -> None:
        self.location = LocationFactory(id=2, name='Iceland')

    def test_serialization(self):
        serializer = self.serializer_cls(instance=self.location)

        self.assertDictEqual(serializer.data, {
            'id': 2,
            'name': 'Iceland'
        })
