from django.db.utils import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from leagues.models import League
from leagues.tests import LeagueFactory
from sports.tests import SportFactory


class LeagueModelTests(BaseTestCase):
    def setUp(self):
        self.ice_hockey = SportFactory.create(name='Ice Hockey')

    def test_default_ordering(self):
        liahl = LeagueFactory(name='Long Island Amateur Hockey League')
        nhl = LeagueFactory(name='National Hockey League')
        expected = [liahl, nhl]
        self.assertListEqual(list(League.objects.all()), expected)

    def test_to_string(self):
        nhl = LeagueFactory.create(name='National Hockey League', sport=self.ice_hockey)
        self.assertEqual(str(nhl), 'National Hockey League')

    def test_name_different_sports(self):
        # No error should be thrown, sports are different
        LeagueFactory.create(name='My League', sport=self.ice_hockey)
        LeagueFactory.create(name='My League', sport=SportFactory.create(name='My Other Sport'))

    def test_name_unique_with_sport(self):
        League.objects.create(name='National Hockey League', sport=self.ice_hockey)
        with self.assertRaises(IntegrityError):
            League.objects.create(name='National Hockey League', sport=self.ice_hockey).full_clean(
                exclude=['abbreviated_name'])

    def test_abbreviated_name_lowercase(self):
        # Make sure first letters are capitalized
        nhl = LeagueFactory.create(name='national Hockey league', sport=self.ice_hockey)
        nhl.full_clean(exclude=['abbreviated_name'])
        self.assertEqual(nhl.abbreviated_name, 'NHL')

    def test_abbreviated_name_normal(self):
        liahl = LeagueFactory.create(name='Long Island Amateur Hockey League', sport=self.ice_hockey)
        liahl.full_clean(exclude=['abbreviated_name'])
        self.assertEqual(liahl.abbreviated_name, 'LIAHL')

    def test_abbreviated_name_one_word(self):
        fake_league = LeagueFactory.create(name='National', sport=self.ice_hockey)
        fake_league.full_clean(exclude=['abbreviated_name'])
        self.assertEqual(fake_league.abbreviated_name, 'N')

    def test_abbreviated_name_extra_whitespace(self):
        fake_league = LeagueFactory.create(name=' League With  Extra  Space', sport=self.ice_hockey)
        fake_league.full_clean(exclude=['abbreviated_name'])
        self.assertEqual(fake_league.abbreviated_name, 'LWES')

    def test_slug_generation(self):
        nhl = LeagueFactory(name='National Hockey League', sport=self.ice_hockey)
        self.assertEqual(nhl.slug, 'nhl')

    def test_slug_unique_with_sport(self):
        LeagueFactory.create(name='National Hockey League', sport=self.ice_hockey)
        with self.assertRaises(IntegrityError):
            # Below has the same abbreviated name and slug, so should throw an error
            LeagueFactory(name='Notareal Hockey League', sport=self.ice_hockey)
