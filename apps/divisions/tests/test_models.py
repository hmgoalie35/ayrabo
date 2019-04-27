from django.db.utils import IntegrityError

from ayrabo.utils.testing import BaseTestCase
from divisions.models import Division
from divisions.tests import DivisionFactory
from leagues.tests import LeagueFactory


class DivisionModelTests(BaseTestCase):
    def test_default_ordering(self):
        mm = DivisionFactory(name='Midget Minor')
        mites = DivisionFactory(name='Mites')
        peewee = DivisionFactory(name='Pee Wee')
        expected = [mm, mites, peewee]
        self.assertListEqual(list(Division.objects.all()), expected)

    def test_to_string(self):
        metro_division = DivisionFactory(name='Metropolitan Division')
        self.assertEqual(str(metro_division), 'Metropolitan Division')

    def test_duplicate_division_name_same_league(self):
        liahl = LeagueFactory(name='Long Island Amateur Hockey League')
        Division.objects.create(name='Default', league=liahl)
        with self.assertRaises(IntegrityError):
            Division.objects.create(name='Default', league=liahl)

    def test_duplicate_division_name_different_league(self):
        # shouldn't throw an error
        liahl = LeagueFactory(name='Long Island Amateur Hockey League')
        nhl = LeagueFactory(name='National Hockey League')
        DivisionFactory(name='Default', league=liahl)
        DivisionFactory(name='Default', league=nhl)

    def test_slug_generation(self):
        liahl = LeagueFactory(name='Long Island Amateur Hockey League')
        division_name = 'Midget Minor AA'
        midget_minor_aa = DivisionFactory(name=division_name, league=liahl)
        self.assertEqual(midget_minor_aa.slug, 'midget-minor-aa')

    def test_slug_unique_for_league(self):
        liahl = LeagueFactory(name='Long Island Amateur Hockey League')
        division_name = 'Midget Minor AA'
        Division.objects.create(name=division_name, league=liahl)
        with self.assertRaises(IntegrityError):
            Division.objects.create(name=division_name, league=liahl)
