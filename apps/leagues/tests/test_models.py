from django.test import TestCase
from .factories.LeagueFactory import LeagueFactory
from leagues.models import League
from django.db.utils import IntegrityError


class LeagueModelTests(TestCase):

    def test_default_ordering(self):
        leagues = LeagueFactory.create_batch(5)
        self.assertListEqual(leagues, list(League.objects.all()))

    def test_to_string(self):
        nhl = LeagueFactory.create(full_name='National Hockey League')
        self.assertEqual(str(nhl), 'National Hockey League')

    def test_unique_full_name(self):
        LeagueFactory.create(full_name='National Hockey League')
        with self.assertRaises(IntegrityError, msg='UNIQUE constraint failed: leagues_league.full_name'):
            LeagueFactory.create(full_name='National Hockey League')

    def test_abbreviated_name_lowercase(self):
        # Make sure first letters are capitalized
        nhl = LeagueFactory.create(full_name='national Hockey league')
        self.assertEqual(nhl.abbreviated_name, 'NHL')

    def test_abbreviated_name_normal(self):
        liahl = LeagueFactory.create(full_name='Long Island Amateur Hockey League')
        self.assertEqual(liahl.abbreviated_name, 'LIAHL')

    def test_abbreviated_name_one_word(self):
        fake_league = LeagueFactory.create(full_name='National')
        self.assertEqual(fake_league.abbreviated_name, 'N')

    def test_abbreviated_name_extra_whitespace(self):
        fake_league = LeagueFactory.create(full_name=' League With  Extra  Space')
        self.assertEqual(fake_league.abbreviated_name, 'LWES')
