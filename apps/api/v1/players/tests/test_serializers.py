from ayrabo.utils.testing import BaseAPITestCase
from players.models import HockeyPlayer
from players.tests import HockeyPlayerFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory
from users.tests import UserFactory
from ..serializers import HockeyPlayerSerializer


class HockeyPlayerSerializerTests(BaseAPITestCase):
    serializer_cls = HockeyPlayerSerializer

    def test_data(self):
        user = UserFactory(id=1, first_name='Michael', last_name='Scott')
        sport = SportFactory(id=1)
        team = TeamFactory(id=1, division__league__sport=sport)
        player = HockeyPlayerFactory(id=1, user=user, sport=sport, team=team, jersey_number=23, is_active=True,
                                     position=HockeyPlayer.CENTER, handedness=HockeyPlayer.LEFT)

        data = self.serializer_cls(instance=player).data
        self.assertDictEqual(data, {
            'id': 1,
            'user': {
                'id': 1,
                'first_name': 'Michael',
                'last_name': 'Scott'
            },
            'sport': 1,
            'team': 1,
            'jersey_number': 23,
            'is_active': True,
            'position': 'C',
            'handedness': 'Left'
        })
