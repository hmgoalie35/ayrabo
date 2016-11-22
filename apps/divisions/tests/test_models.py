from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from divisions.models import Division
from leagues.tests import LeagueFactory
from .factories.DivisionFactory import DivisionFactory


class DivisionModelTests(TestCase):
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
        liahl = LeagueFactory(full_name='Long Island Amateur Hockey League')
        DivisionFactory(name='Default', league=liahl)
        with self.assertRaises(IntegrityError):
            DivisionFactory(name='Default', league=liahl)

    def test_duplicate_division_name_different_league(self):
        # shouldn't throw an error
        liahl = LeagueFactory(full_name='Long Island Amateur Hockey League')
        nhl = LeagueFactory(full_name='National Hockey League')
        DivisionFactory(name='Default', league=liahl)
        DivisionFactory(name='Default', league=nhl)

    def test_slug_generation(self):
        liahl = LeagueFactory(full_name='Long Island Amateur Hockey League')
        division_name = 'Midget Minor AA'
        midget_minor_aa = DivisionFactory(name=division_name, league=liahl)
        self.assertEqual(midget_minor_aa.slug, slugify(division_name))

    def test_slug_unique_for_league(self):
        liahl = LeagueFactory(full_name='Long Island Amateur Hockey League')
        division_name = 'Midget Minor AA'
        DivisionFactory(name=division_name, league=liahl)
        with self.assertRaises(IntegrityError):
            DivisionFactory(name=division_name, league=liahl)
