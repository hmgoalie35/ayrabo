from ayrabo.utils.testing import BaseAPITestCase
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory
from sports.tests import SportFactory
from ..serializers import DivisionSerializer


class DivisionSerializerTests(BaseAPITestCase):
    serializer_cls = DivisionSerializer

    def setUp(self):
        self.ice_hockey = SportFactory(name='Ice Hockey')
        self.liahl = LeagueFactory(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        self.mm_aa = DivisionFactory(id=1, name='Midget Minor AA', league=self.liahl)

    def test_serialization(self):
        serializer = self.serializer_cls(instance=self.mm_aa)

        self.assertDictEqual(serializer.data, {
            'id': 1,
            'name': 'Midget Minor AA'
        })
