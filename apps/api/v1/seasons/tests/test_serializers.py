from users.tests import UserFactory
from divisions.tests import DivisionFactory
from ayrabo.utils.testing import BaseAPITestCase
from leagues.tests import LeagueFactory
from players.tests import HockeyPlayerFactory
from seasons.tests import HockeySeasonRosterFactory, SeasonFactory
from sports.tests import SportFactory
from teams.tests import TeamFactory
from ..serializers import HockeySeasonRosterSerializer


class HockeySeasonRosterSerializerTests(BaseAPITestCase):
    serializer_cls = HockeySeasonRosterSerializer

    def test_data(self):
        sport = SportFactory(id=1, name='Ice Hockey')
        league = LeagueFactory(sport=sport, name='Long Island Amateur Hockey League')
        division = DivisionFactory(name='Midget Minor AA', league=league)
        team = TeamFactory(id=1, name='Green Machine Icecats', division=division)
        season = SeasonFactory(id=1, league=league)

        user1 = UserFactory(id=1, first_name='Pavel', last_name='Datsyuk')
        user2 = UserFactory(id=2, first_name='John', last_name='Tavares')
        player1 = HockeyPlayerFactory(id=1, user=user1, team=team, sport=sport, jersey_number=13, position='LW',
                                      handedness='Left')
        player2 = HockeyPlayerFactory(id=2, user=user2, team=team, sport=sport, jersey_number=91, position='C',
                                      handedness='Left')
        roster = HockeySeasonRosterFactory(id=1, name='Bash Brothers', default=False, season=season,
                                           players=[player1, player2])
        data = self.serializer_cls(roster).data
        self.assertDictEqual(data, {
            'id': 1,
            'name': 'Bash Brothers',
            'default': False,
            'season': 1,
            'players': [
                {
                    'id': 1,
                    'user': {
                        'id': 1,
                        'first_name': 'Pavel',
                        'last_name': 'Datsyuk',
                    },
                    'sport': 1,
                    'team': 1,
                    'jersey_number': 13,
                    'is_active': True,
                    'position': 'LW',
                    'handedness': 'Left',
                },
                {
                    'id': 2,
                    'user': {
                        'id': 2,
                        'first_name': 'John',
                        'last_name': 'Tavares',
                    },
                    'sport': 1,
                    'team': 1,
                    'jersey_number': 91,
                    'is_active': True,
                    'position': 'C',
                    'handedness': 'Left',
                }
            ],
        })
